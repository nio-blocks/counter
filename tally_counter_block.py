from nio.signal.base import Signal
from nio.properties import VersionProperty
from .counter_block import Counter


class TallyCounter(Counter):

    """ A block that counts the number of signals
    that are processed by it.

    Enriches incoming signals with `tally`, including a key for each
    unique evaluation of `group_by` since the last `reset()`. The value of
    each key is the `cumulative_count` for that `group`.

    """
    version = VersionProperty("0.2.0")

    def process_group(self, signals, key):
        """ Executed on each group of incoming signal objects.
        Increments the appropriate count and generates an informative
        output signal.

        """
        count = self._get_count_from_signals(signals)

        self.logger.debug(
            "Ready to process {} signals in group {}".format(count, key)
        )
        self._cumulative_count[key] = self._cumulative_count.get(key, 0)
        self._cumulative_count[key] += count
        enriched_signal = self.get_output_signal({
            "tally": self._cumulative_count,
            "count": count,
            "group": key
        }, signals[0])
        return [enriched_signal]
