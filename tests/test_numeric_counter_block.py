from unittest.mock import patch
from ..numeric_counter_block import NumericCounter
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal


@patch(NumericCounter.__module__ + '.NumericCounter._backup')
class TestCounter(NIOBlockTestCase):

    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    def test_count(self, back_patch):
        """ Make sure we use the passed counts and not signal lengths """
        block = NumericCounter()
        self.configure_block(block, {
            'count_expr': '{{$test_count}}'
        })
        block.start()
        block.process_signals([Signal({'test_count': 1})])
        block.process_signals([Signal({'test_count': 2})])
        block.process_signals([Signal({'test_count': 3})])
        self.assertEqual(block._cumulative_count['null'], 6)
        self.assert_num_signals_notified(3)
        block.stop()

    def test_count_bad_val(self, back_patch):
        """ Make sure bad values are counted as 0 """
        block = NumericCounter()
        self.configure_block(block, {
            'count_expr': '{{$test_count}}'
        })
        block.start()
        block.process_signals([Signal({'test_count': 1})])
        block.process_signals([
            Signal({'test_count': 2}), Signal({'test_count': 3})])
        block.process_signals([
            Signal({'test_count': 3}), Signal({'bad_test_count': 2})])
        block.process_signals([Signal({'bad_test_count': 3})])

        # We only add up the ones that have the valid count attribute
        # 1 + 2 + 3 + 3
        self.assertEqual(block._cumulative_count['null'], 9)

        # One of the process signals only had zeroes, shouldn't be notified
        self.assert_num_signals_notified(3)
        block.stop()

    def test_count_groups(self, back_patch):
        """ Make sure we get the group by functionality in this block too """
        block = NumericCounter()
        self.configure_block(block, {
            'count_expr': '{{$test_count}}',
            'group_by': '{{$group}}',
            'log_level': 'DEBUG'
        })
        block.start()
        block.process_signals([Signal({'group': 'A', 'test_count': 1})])
        block.process_signals([Signal({'group': 'A', 'test_count': 2})])
        block.process_signals([Signal({'group': 'B', 'test_count': 20})])
        block.process_signals([Signal({'group': 'B', 'test_count': 30})])
        block.process_signals([Signal({'group': 'A', 'test_count': 3})])
        self.assertEqual(block._cumulative_count['A'], 6)
        self.assertEqual(block._cumulative_count['B'], 50)
        self.assert_num_signals_notified(5)
        block.stop()

    def test_no_zeroes(self, back_patch):
        """ Make sure the block doesn't notify zero counts """
        block = NumericCounter()
        self.configure_block(block, {
            'count_expr': '{{$test_count}}'
        })
        block.start()
        block.process_signals([Signal({'test_count': 1})])
        block.process_signals([Signal({'test_count': 2})])
        block.process_signals([Signal({'test_count': 0})])
        block.process_signals([Signal({'test_count': 3})])
        block.process_signals([Signal({'test_count': 0})])
        self.assertEqual(block._cumulative_count['null'], 6)
        # Even though 5 signals sent, only 3 sent out (no zeroes!)
        self.assert_num_signals_notified(3)
        block.stop()
