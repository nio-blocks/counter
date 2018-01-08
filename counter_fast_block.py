from copy import copy
from time import time as _time
from threading import Lock

from nio.block.base import Block
from nio.command import command
from nio.signal.base import Signal
from nio.properties import BoolProperty, TimeDeltaProperty, \
    PropertyHolder, ObjectProperty, VersionProperty
from nio.modules.scheduler import Job


def total_seconds(interval):
    return (interval.days * 24 * 60 * 60 +
            interval.seconds + interval.microseconds * 1e-6)


class FrequencyTracker(object):
    """ Helper class for tracking the frequency of incoming signals

    Args:
        period (int): The period (in seconds) over which to calculate
            signal frequencies.

    """
    version = VersionProperty("0.1.1")

    def __init__(self, period=1):
        self.signals = []
        self._signals_lock = Lock()
        self.period = period
        self._start_time = _time()

    def record(self, count):
        """ Record a signal count.

        """
        with self._signals_lock:
            self.signals.append((_time(), count))

    def get_frequency(self):
        """ Calculate and return the signal frequency.

        Aggregate the number of signals over the configured period
        and find the frequency.

        """
        ctime = None
        # update signals to only include ones that are inside of the
        # current period
        with self._signals_lock:
            ctime = _time()
            self.signals = [(ct, c) for (ct, c) in self.signals
                            if ctime - ct < self.period]
            signals = copy(self.signals)

        total_count = sum([grp[1] for grp in signals])
        uptime = ctime - self._start_time

        if uptime < self.period:
            return total_count / uptime

        return total_count / self.period


class Frequency(PropertyHolder):
    """ An object to encapsulate frequency reporting configuration.

    Properties:
        enabled (bool): Is frequency reporting enabled?
        report_interval (timedelta): The interval at which to
            report the frequency.
        averaging_interval (timedelta): The period over which
            frequencies are calculated.

    """
    enabled = BoolProperty(default=False, title="Report Frequency?")
    report_interval = TimeDeltaProperty(default={"seconds": 1},
                                        title="Report Interval")
    averaging_interval = TimeDeltaProperty(default={"seconds": 5},
                                           title="Averaging Interval")


@command("value")
@command("reset")
class CounterFast(Block):

    version = VersionProperty("0.1.1")
    frequency = ObjectProperty(
        Frequency, title="Report Freqency", default=Frequency())

    def configure(self, context):
        super().configure(context)
        self._cumulative_count = 0
        self._cumulative_count_lock = Lock()

        if self.frequency().enabled():
            self._tracker = FrequencyTracker(
                total_seconds(self.frequency().averaging_interval()))

    def start(self):
        if self.frequency().enabled():
            self._job = Job(self.report_frequency,
                            self.frequency().report_interval(), True)

    def process_signals(self, signals):
        count = len(signals)
        self.logger.debug("Ready to process {} signals".format(count))

        with self._cumulative_count_lock:
            if self.frequency().enabled():
                self._tracker.record(count)
            self._cumulative_count += count
            cumulative_count = self._cumulative_count
        signal = Signal({
            "count": count,
            "cumulative_count": cumulative_count,
        })
        self.notify_signals([signal])

    def report_frequency(self):
        self.logger.debug("Reporting signal frequency")
        signal = Signal({"count_frequency": self._tracker.get_frequency()})
        self.notify_signals([signal])

    def stop(self):
        try:
            self._job.cancel()
        except AttributeError:
            pass
        super().stop()

    def reset(self):
        with self._cumulative_count_lock:
            self._cumulative_count = 0
        return True

    def value(self):
        return self._cumulative_count
