from nio.testing.block_test_case import NIOBlockTestCase
from nio import Signal

from ..tally_counter_block import TallyCounter


class TestCounter(NIOBlockTestCase):

    def test_tally(self):
        """ Test that all groups are notified inside `tally` """
        blk = TallyCounter()
        self.configure_block(blk, {
            'group_by': '{{ $foo }}',
        })
        blk.start()

        blk.process_signals([
            Signal({'foo': 'bar'}),
        ])
        self.assert_last_signal_list_notified([
            Signal({
                'count': 1,
                'group': 'bar',
                'tally': {
                    'bar': 1,
                },
            })
        ])

        blk.process_signals([
            Signal({'foo': 'bar'}),
            Signal({'foo': 'baz'}),
        ])
        self.assert_last_signal_list_notified([
            Signal({
                'count': 1,
                'group': 'bar',
                'tally': {
                    'bar': 2,
                    'baz': 1,
                },
            }),
            Signal({
                'count': 1,
                'group': 'baz',
                'tally': {
                    'bar': 2,
                    'baz': 1,
                },
            }),
        ])
