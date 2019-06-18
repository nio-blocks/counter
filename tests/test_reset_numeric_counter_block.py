from nio import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..reset_numeric_counter_block import ResettableNumericCounter


class TestResetCounter(NIOBlockTestCase):

    def test_reset_count(self):
        block = ResettableNumericCounter()
        self.configure_block(block, {})
        block.start()
        block.process_signals([Signal({'count': 1})])
        block.process_signals([Signal({'count': 2})])
        block.process_signals([Signal({'count': 3})])
        self.assertEqual(block._cumulative_count[None], 6)
        self.assert_num_signals_notified(3)
        block.process_signals([Signal()], input_id='reset')
        self.assertEqual(block._cumulative_count[None], 0)
        block.process_signals([Signal({'count': 1})])
        block.process_signals([Signal({'count': -4})])
        self.assert_num_signals_notified(6)
        self.assertEqual(block._cumulative_count[None], -3)
        block.stop()

    def test_reset_count_groups(self):
        block = ResettableNumericCounter()
        self.configure_block(block, {
            "group_by": "{{ $group }}",
        })
        block.start()
        block.process_signals([Signal({'count': 1, 'group': 'A'})])
        block.process_signals([Signal({'count': 1, 'group': 'B'})])
        block.process_signals([Signal({'count': 2, 'group': 'A'})])
        self.assertEqual(block._cumulative_count['A'], 3)
        self.assertEqual(block._cumulative_count['B'], 1)
        self.assert_num_signals_notified(3)
        block.process_signals([Signal({'group': 'A'})], input_id='reset')
        self.assertEqual(block._cumulative_count['A'], 0)
        self.assertEqual(block._cumulative_count['B'], 1)
        # Only one reset signal even through there's two groups
        self.assert_num_signals_notified(4)
        block.stop()
