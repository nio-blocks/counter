from nio.block import input
from nio.properties import VersionProperty

from .counter_block import Counter


@input('count', label='Count', default=True, order=1)
@input('reset', label='Reset', order=2)
class ResettableCounter(Counter):

    """ The same as the counter block but with an input to reset a
    cumulative count """
    version = VersionProperty("0.2.0")

    def process_signals(self, signals, input_id='count'):
        if input_id == 'reset':
            self.notify_signals(self.for_each_group(
                self.reset_group_from_signals, signals))
        else:
            super().process_signals(signals)

    def reset_group_from_signals(self, signals, key):
        """ Reset the groups inlcuded in the list of incoming signals.

        A method that takes signals as the first argument for use in
        the group by mixin's for_each_group method.
        """
        try:
            return self.reset_group(key)
        except KeyError:
            # resetting a group that hasn't been counted yet,
            # create it with a count of 0 and try again
            self._cumulative_count[key] = 0
            return self.reset_group(key)
