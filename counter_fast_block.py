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

from time import time as _time


def total_seconds(interval):
    return (interval.days * 24 * 60 * 60 +
            interval.seconds + interval.microseconds * 1e-6)


class FrequencyTracker(object):

    def __init__(self, period=1):
        self.signals = []
        self.period = period
        self.last_get = _time()
        self._start_time = self.last_get

    def record(self, count):
        ctime = _time()
        self.signals.append((ctime, count))

    def get_frequency(self):
        period = self.period
        signals = self.signals
        ctime = _time()
        # only include signals that are inside of the current period
        signals = [(ct, c) for (ct, c) in signals if ctime - ct < period]

        if not signals:
            return 0
        if len(signals) < 2:
            return signals[0][1] / self.period
        assert signals[-1][0] - signals[0][0] < self.period
        count = sum(tuple(zip(*signals))[1])

        elapsed = ctime - self._start_time
        if elapsed > self.period:
            return count / self.period
        else:
            return count / elapsed


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
