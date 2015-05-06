from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from ..counter_block import Counter
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from nio.modules.threading import Event, spawn
import time


class EventCounter(Counter):

    def __init__(self, event):
        super().__init__()
        self._event = event

    def reset(self, cron=False):
        super().reset(cron)
        self._event.set()


class LieCounter(Counter):

    def __init__(self, event):
        super().__init__()
        self._event = event

    def start(self, last_reset):
        self.reset_info.resetting = False
        super().start()
        self._last_reset = last_reset
        self._schedule_reset()


@patch(Counter.__module__ + '.Counter._backup')
class TestCounter(NIOBlockTestCase):

    def get_test_modules(self):
        return self.ServiceDefaultModules + ['persistence']

    def test_count(self, back_patch):
        block = Counter()
        self.configure_block(block, {})
        block.start()
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        self.assertEqual(block._cumulative_count['null'], 3)
        self.assert_num_signals_notified(3)
        block.stop()

    def test_count_simultanious(self, back_patch):
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
            self.assertEqual(block._cumulative_count['null'],
                             100000 * process_times)
            self.assert_num_signals_notified(process_times)
        # wait for spawns to be done
        while spawns:
            time.sleep(0.1)
            spawns = tuple(s for s in spawns if s.isAlive())
        # make sure everything works as expected
        self.assertEqual(block._cumulative_count['null'],
                         100000 * process_times)
        self.assert_num_signals_notified(process_times)
        block.stop()

    def test_reset(self, back_patch):
        block = Counter()
        self.configure_block(block, {})
        block.start()
        block.process_signals([Signal()])
        block.process_signals([Signal()])
        block.reset()
        block.process_signals([Signal()])
        self.assertEqual(block._cumulative_count['null'], 1)
        block.stop()

    def test_interval_reset(self, back_patch):
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
        self.assertEqual(block._cumulative_count['null'], 0)
        block.stop()

    def test_cron_sched(self, back_patch):
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
        self.assertEqual(block._cumulative_count['null'], 1)
        e.wait(1.25)
        self.assertEqual(block._cumulative_count['null'], 0)

    def test_cron_missed_reset(self, back_patch):
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
        block.reset.assert_called_once()

    def test_groups(self, back_patch):
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
            Signal({'qux': 'ly'})
        ])
        self.assertEqual(block._cumulative_count[''], 1)
        self.assertEqual(block._cumulative_count['bar'], 1)
        self.assertEqual(block._cumulative_count['baz'], 1)
        e.wait(2)
        for k in block._cumulative_count:
            self.assertEqual(block._cumulative_count[k], 0)
        block.stop()
