from copy import copy
from time import time as _time
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.command import command
from nio.common.signal.base import Signal
from nio.metadata.properties.bool import BoolProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.object import ObjectProperty
from nio.modules.threading import Lock
from nio.modules.scheduler import Job


def total_seconds(interval):
    return (interval.days * 24 * 60 * 60 +
            interval.seconds + interval.microseconds * 1e-6)


class FrequencyTracker(object):

    def __init__(self, period=1):
        self.signals = []
        self._signals_lock = Lock()
        self.period = period
        self._start_time = _time()

    def record(self, count):
        with self._signals_lock:
            self.signals.append((_time(), count))

    def get_frequency(self):
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
    enabled = BoolProperty(default=False, title="Report Frequency?")
    report_interval = TimeDeltaProperty(default={"seconds": 1},
                                        title="Report Interval")
    averaging_interval = TimeDeltaProperty(default={"seconds": 5},
                                           title="Averaging Interval")


@command("reset")
@Discoverable(DiscoverableType.block)
class CounterFast(Block):
    frequency = ObjectProperty(Frequency, title="Report Freqency")

    def configure(self, context):
        super().configure(context)
        self._cumulative_count = 0
        self._cumulative_count_lock = Lock()

        if self.frequency.enabled:
            self._tracker = FrequencyTracker(
                total_seconds(self.frequency.averaging_interval))

    def start(self):
        if self.frequency.enabled:
            self._job = Job(self.report_frequency,
                            self.frequency.report_interval, True)

    def process_signals(self, signals):
        count = len(signals)
        with self._cumulative_count_lock:
            if self.frequency.enabled:
                self._tracker.record(count)
            self._cumulative_count += count
            cumulative_count = self._cumulative_count
        signal = Signal({
            "count": count,
            "cumulative_count": cumulative_count,
        })
        self.notify_signals([signal])

    def report_frequency(self):
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
