from nio.block import input
from nio.properties import VersionProperty

from .counter_block import Counter


@input('count', label='Count', default=True, order=1)
@input('reset', label='Reset', order=2)
class ResettableCounter(Counter):

    """ The same as the counter block but with an input to reset a
    cumulative count """
    version = VersionProperty("0.3.1")

    def process_signals(self, signals, input_id='count'):
        if input_id == 'reset':
            try:
                signals = self.for_each_group(
                    self.reset_group_from_signals, signals)
            except AttributeError:
                # group evaluation of reset signal failed
                self.for_each_group(self.reset_group)
            if self.emit_on_reset():
                self.notify_signals(signals)
        else:
            super().process_signals(signals)

    def reset_group_from_signals(self, signals, key):
        """ Reset the groups inlcuded in the list of incoming signals.

        A method that takes signals as the first argument for use in
        the group by mixin's for_each_group method.
        """
        return self.reset_group(key)
