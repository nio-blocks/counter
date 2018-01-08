from datetime import datetime, timedelta
from enum import Enum

from nio.block.base import Block
from nio.signal.base import Signal
from nio.command import command
from nio.properties import SelectProperty, TimeDeltaProperty, \
    ObjectProperty, PropertyHolder, IntProperty, BoolProperty, VersionProperty
from nio.modules.scheduler import Job
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.block.mixins.group_by.group_by import GroupBy
from nio.block.mixins.persistence.persistence import Persistence


class ResetScheme(Enum):
    INTERVAL = 0
    CRON = 1


class Time(PropertyHolder):
    hour = IntProperty(title='Hour', default=0)
    minute = IntProperty(title='Minute', default=0)
    pm = BoolProperty(title='PM', default=False)


class ResetInfo(PropertyHolder):
    resetting = BoolProperty(title='Resetting', default=False)
    scheme = SelectProperty(ResetScheme, default=ResetScheme.INTERVAL,
                            title='Reset Scheme')
    at = ObjectProperty(Time, title="Time (UTC)", default=Time())
    interval = TimeDeltaProperty(title='Reset Interval', default=timedelta(0))


@command("reset")
class Counter(EnrichSignals, Persistence, GroupBy, Block):

    """ A block that counts the number of signals
    that are processed by it.

    Outputs 'count' as the number of signals in
    the currently list of signals and 'cumulative_count'
    as the total since the block was started.

    Properties:
        group_by (Property): The value by which signals are grouped.
        reset_info (ResetInfo):
            resetting (bool): Does the counter reset?
            scheme (ResetScheme): The reset mode (CRON or INTERVAL)
            at (Time): The hour (int), minute (int), and pm (bool) at
                which the counter should be reset. Corresponds to CRON mode.
            interval (timedelta): The interval at which the counter should
                be reset. Corresponds to INTERVAL mode.

    """
    reset_info = ObjectProperty(ResetInfo, title='Reset Info',
                                default=ResetInfo())
    version = VersionProperty("0.1.1")

    def __init__(self):
        super().__init__()
        self._cumulative_count = {}
        self._reset_job = None
        self._last_reset = None

    def start(self):
        if self.reset_info().resetting():
            self._schedule_reset()

    def persisted_values(self):
        """Persist values with block mixin"""
        return ["_cumulative_count", "_last_reset", "_groups"]

    def _schedule_reset(self):
        """ Determines the appropriate time for the next counter reset based
        on the reset scheme setting and the stored 'last_reset' datetime.

        Note that a scheduled reset missed on account of service downtime
        will be executed upon startup.

        """
        if self.reset_info().scheme() == ResetScheme.INTERVAL:

            self.logger.debug(
                "Configuring Counter to reset on an interval of {}".format(
                    self.reset_info().interval())
            )

            self._reset_job = Job(
                self.reset,
                self.reset_info().interval(),
                True
            )

            # if it's been longer than the configured interval since our last
            # reset, get on with it
            if self._last_reset is not None \
                    and datetime.utcnow() - self._last_reset \
                    > self.reset_info().interval():
                self.reset()

        if self.reset_info().scheme() == ResetScheme.CRON:

            self.logger.debug(
                "Configuring Counter to reset at {}:{} {}".format(
                    self.reset_info().at().hour(),
                    self.reset_info().at().minute(),
                    'p.m.' if self.reset_info().at().pm() else 'a.m.')
            )

            now = datetime.utcnow()
            next_reset = self._calculate_next(now)

            # if we missed the scheduled reset today, do it now and
            # push the next reset time back a day
            if next_reset < datetime.utcnow():
                if self._last_reset is not None and \
                   self._last_reset < next_reset:
                    self.logger.debug(
                        "Missed a scheduled counter reset. Performing now"
                    )
                    self.reset()

                next_reset += timedelta(days=1)

            time_til_next_reset = next_reset - now

            self._reset_job = Job(
                self.reset,
                time_til_next_reset,
                False,
                cron=True
            )

    def _calculate_next(self, now):
        """ Calculate the time for the next reset event

        """
        year, month, day = (now.year, now.month, now.day)
        minute = self.reset_info().at().minute()
        hour = self.reset_info().at().hour()
        if self.reset_info().at().pm():
            hour += 12

        date = datetime(year, month, day, hour, minute)

        return date

    def process_signals(self, signals):
        self.notify_signals(self.for_each_group(self.process_group, signals))

    def process_group(self, signals, key):
        """ Executed on each group of incoming signal objects.
        Increments the appropriate count and generates an informative
        output signal.

        """
        count = self._get_count_from_signals(signals)

        # If count is None, the block must not want to send any signals
        # This is in place so that the NumericCounter can choose whether or
        # not to send 'zero' counts
        if count is None:
            self.logger.debug("Ignoring count - not notifying")
            return

        self.logger.debug(
            "Ready to process {} signals in group {}".format(count, key)
        )
        self._cumulative_count[key] = self._cumulative_count.get(key, 0)
        self._cumulative_count[key] += count
        enriched_signal = self.get_output_signal({
            "count": count,
            "cumulative_count": self._cumulative_count[key],
            "group": key
        }, signals[0])
        return [enriched_signal]

    def _get_count_from_signals(self, signals):
        """ Get the count we want given a list of signals.

        This block can be overridden in sub blocks. If the block returns
        None, then no count signal will be notified.
        """
        return len(signals)

    def reset(self, cron=False):

        # In the 'CRON' scheme, the first scheduling will be at an odd
        # interval (i.e. scheduled time tmrw - current time). In this case,
        # we want to cancel that job and put ourselves on a 24h interval
        if cron:
            self._reset_job = Job(
                self.reset,
                timedelta(hours=24),
                True
            )
        self.notify_signals(self.for_each_group(self.reset_group))
        self._last_reset = datetime.utcnow()

    def reset_group(self, key):
        self.logger.debug(
            "Resetting the Counter ({}:{})".format(
                key, self._cumulative_count[key])
        )
        signal = Signal({
            "count": 0,
            "cumulative_count": self._cumulative_count[key],
            "group": key
        })

        # set the cumulative count, last reset, and write both to disk
        self._cumulative_count[key] = 0
        # finally, send the signal with the counts at reset time
        return [signal]
