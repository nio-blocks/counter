from nio import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..reset_counter_block import ResettableCounter


class TestResetCounter(NIOBlockTestCase):

    def test_reset_count(self):
        block = ResettableCounter()
        self.configure_block(block, {})
        block.start()
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        self.assertEqual(block._cumulative_count[None], 3)
        self.assert_num_signals_notified(3)
        block.process_signals([Signal()], input_id='reset')
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        self.assert_num_signals_notified(6)
        self.assertEqual(block._cumulative_count[None], 2)
        block.stop()

    def test_reset_count_groups(self):
        block = ResettableCounter()
        self.configure_block(block, {
            "group_by": "{{ $group_key }}",
        })
        block.start()
        block.process_signals([Signal({'group_key': 'A'})])
        block.process_signals([Signal({'group_key': 'B'})])
        block.process_signals([Signal({'group_key': 'A'})])
        self.assertEqual(block._cumulative_count['A'], 2)
        self.assertEqual(block._cumulative_count['B'], 1)
        self.assert_num_signals_notified(3)
        block.process_signals([Signal({'group_key': 'A'})], input_id='reset')
        self.assertEqual(block._cumulative_count['A'], 0)
        self.assertEqual(block._cumulative_count['B'], 1)
        # Only one reset signal even through there's two groups
        self.assert_num_signals_notified(4)
        # an unknown group is reset
        block.process_signals([Signal({'group_key': 'C'})], input_id='reset')
        block.stop()
