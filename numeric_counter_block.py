from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty, BoolProperty, \
    VersionProperty
from .counter_block import Counter


@Discoverable(DiscoverableType.block)
class NumericCounter(Counter):

    version = VersionProperty('0.1.0')
    count_expr = ExpressionProperty(
        title='Count Expression', default='{{$count}}')
    send_zeroes = BoolProperty(title='Send Zero Counts', default=True)

    def _get_count_from_signals(self, signals):
        """ Get counts from signals.

        In this block, we loop through the signals and grab the passed counts
        rather than use the length of the signal list.

        Replace invalidly passed counts with zeroes.
        """
        count = 0
        for sig in signals:
            try:
                # Grab the passed count from this signal
                sig_count = int(self.count_expr(sig))
            except:
                self._logger.warning(
                    "Unable to determine count for {}".format(sig))
                sig_count = 0
            count += sig_count

        if not self.send_zeroes and count == 0:
            # If we don't want to send zeroes, return None if it's zero
            # so that the count doesn't get notified
            return None

        return count
