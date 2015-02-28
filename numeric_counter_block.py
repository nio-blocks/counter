from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty
from .counter_block import Counter


@Discoverable(DiscoverableType.block)
class NumericCounter(Counter):

    count_expr = ExpressionProperty(
        title='Count Expression', default='{{$count}}')

    def _get_count_from_signals(self, signals):
        count = 0
        for sig in signals:
            try:
                sig_count = int(self.count_expr(sig))
            except:
                self._logger.warning(
                    "Unable to determine count for {}".format(sig))
                sig_count = 0
            count += sig_count

        return count
