from unittest.mock import MagicMock
import time
from datetime import datetime, timedelta
from threading import Event

from nio.util.threading.spawn import spawn
from nio.util.discovery import not_discoverable
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal

from ..counter_block import Counter


@not_discoverable
class EventCounter(Counter):

    def __init__(self, event):
        super().__init__()
        self._event = event

    def reset(self, cron=False):
        super().reset(cron)
        self._event.set()


@not_discoverable
class LieCounter(Counter):

    def __init__(self, event):
        super().__init__()
        self._event = event

    def start(self, last_reset):
        self.reset_info.resetting = False
        super().start()
        self._last_reset = last_reset
        self._schedule_reset()


class TestCounter(NIOBlockTestCase):

    def test_count(self):
        block = Counter()
        self.configure_block(block, {})
        block.start()
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        self.assertEqual(block._cumulative_count[None], 3)
        self.assert_num_signals_notified(3)
        block.stop()

    def test_count_simultanious(self):
        block = Counter()
        self.configure_block(block, {})
        block.start()
        signals = list(Signal() for _ in range(100000))
        process_times = 5
        spawns = []
        for _ in range(process_times):
            spawns.append(spawn(block.process_signals, signals))
        # it should take a while to complete
        with self.assertRaises(Exception):
            self.assertEqual(block._cumulative_count[None],
                             100000 * process_times)
            self.assert_num_signals_notified(process_times)
        # wait for spawns to be done
        while spawns:
            time.sleep(0.1)
            spawns = tuple(s for s in spawns if s.isAlive())
        # make sure everything works as expected
        self.assertEqual(block._cumulative_count[None],
                         100000 * process_times)
        self.assert_num_signals_notified(process_times)
        block.stop()

    def test_reset(self):
        block = Counter()
        self.configure_block(block, {})
        block.start()
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        block.reset()
        block.process_signals([Signal()])
        self.assertEqual(block._cumulative_count[None], 1)
        block.stop()

    def test_interval_reset(self):
        e = Event()
        block = EventCounter(e)
        self.configure_block(block, {
            "reset_info": {
                "resetting": True,
                "scheme": "INTERVAL",
                "interval": {
                    "seconds": 1
                }
            }
        })
        block.start()
        block.process_signals([Signal(), Signal()])
        e.wait(2)
        self.assertEqual(block._cumulative_count[None], 0)
        block.stop()

    def test_cron_sched(self):
        now = datetime.utcnow()
        e = Event()
        block = EventCounter(e)
        block._calculate_next = MagicMock(
            return_value=now+timedelta(seconds=1))

        # Reset one minute in the future
        reset_at = now + timedelta(minutes=1)
        self.configure_block(block, {
            "reset_info": {
                "resetting": True,
                "scheme": "CRON",
                "at": {
                    "hour": reset_at.hour,
                    "minute": reset_at.minute
                }
            },
        })
        block.start()
        block.process_signals([Signal()])
        self.assertEqual(block._cumulative_count[None], 1)
        e.wait(1.25)
        self.assertEqual(block._cumulative_count[None], 0)

    def test_cron_missed_reset(self):
        now = datetime.utcnow()
        e = Event()
        block = LieCounter(e)
        block.reset = MagicMock()

        # Reset one minute in the past
        reset_at = now - timedelta(minutes=1)
        self.configure_block(block, {
            "log_level": "DEBUG",
            "reset_info": {
                "resetting": True,
                "scheme": "CRON",
                "at": {
                    "hour": reset_at.hour,
                    "minute": reset_at.minute
                }
            },
        })
        block.start(now - timedelta(minutes=10))
        block.process_signals([Signal()])
        e.wait(0.5)
        self.assertEqual(block.reset.call_count, 1)

    def test_groups(self):
        e = Event()
        block = EventCounter(e)
        self.configure_block(block, {
            "reset_info": {
                "resetting": True,
                "scheme": "INTERVAL",
                "interval": {
                    "seconds": 1
                },
            },
            "group_by": "{{$foo}}"
        })
        block.start()
        block.process_signals([
            Signal({'foo': 'bar'}),
            Signal({'foo': 'baz'}),
            Signal({'foo': ''})
        ])
        self.assertEqual(block._cumulative_count[''], 1)
        self.assertEqual(block._cumulative_count['bar'], 1)
        self.assertEqual(block._cumulative_count['baz'], 1)
        e.wait(2)
        for k in block._cumulative_count:
            self.assertEqual(block._cumulative_count[k], 0)
        block.stop()

    def test_persistence(self):
        """ Test that the block uses persistence """
        blk = Counter()
        _time = datetime.utcnow()
        # Set up persistence
        blk._cumulative_count = {"key": 42}
        blk._last_reset = _time
        blk._groups = ["key"]
        self.configure_block(blk, {})
        blk._persistence.save = MagicMock()
        # Confirm that the persisted attrs were loaded from persistence
        self.assertEqual(blk._cumulative_count, {"key": 42})
        self.assertEqual(blk._last_reset, _time)
        self.assertEqual(blk._groups, ["key"])
        # Check that attrs are persisted at the end
        blk.start()
        blk.stop()
        call_args_list = [i[0] for i in blk._persistence.save.call_args_list]
        self.assertTrue(len(call_args_list), 3)
        self.assertTrue(
            "_cumulative_count" in call_args_list[0][0].keys())
        self.assertTrue(
            "_last_reset" in call_args_list[0][0].keys())
        self.assertTrue(
            "_groups" in call_args_list[0][0].keys())
        self.assertEqual(blk._persistence.save.call_count, 1)
