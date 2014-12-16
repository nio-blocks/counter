
from ..counter_fast_block import CounterFast, FrequencyTracker
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.modules.threading import sleep


class TestCounterFast(NIOBlockTestCase):

    def test_count(self):
        blk = CounterFast()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal()])
        blk.process_signals([Signal()])
        blk.process_signals([Signal()])
        blk.process_signals([Signal(), Signal()])
        self.assertEqual(blk._cumulative_count, 5)
        self.assert_num_signals_notified(4)
        blk.stop()

    def test_tracker(self):
        """ Test the accuracy of the frequency tracker """
        tracker = FrequencyTracker()

        sleep(1.5)
        # skip the 1st second

        tracker.record(1)
        tracker.record(2)
        # Should be 1 + 2 in the 2nd second = ~3
        self.assertAlmostEqual(tracker.get_frequency(), 3, 1)

        sleep(1)
        tracker.record(3)
        tracker.record(4)
        # Should be 3+4 in the 3rd second = ~7
        self.assertAlmostEqual(tracker.get_frequency(), 7, 1)
