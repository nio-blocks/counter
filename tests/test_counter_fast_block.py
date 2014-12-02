
from ..counter_fast_block import  CounterFast
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase

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

