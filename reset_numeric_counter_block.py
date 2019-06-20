from nio.block import input
from nio.properties import VersionProperty

from .numeric_counter_block import NumericCounter


@input('count', label='Count', default=True, order=1)
@input('reset', label='Reset', order=2)
class ResettableNumericCounter(NumericCounter):

    """ The same as the numeric counter block but with an input to reset a
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
        return self.reset_group(key)
