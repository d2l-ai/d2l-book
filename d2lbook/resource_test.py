"""
Run multiple instances from terminal to test

python d2lbook/resource_test.py
"""
from d2lbook import resource
import unittest
import time
import logging


def _incorrect_code():
    for i in a:
        print(i)


def _runtime_error():
    return 1 / 0


class TestResource(unittest.TestCase):
    def test_gpus(self):
        self.assertGreaterEqual(len(resource.get_available_gpus()), 0)

    def test_scheduler(self):
        scheduler = resource.Scheduler(num_cpu_workers=2)
        scheduler.add(1, 0, _incorrect_code, ())
        scheduler.add(1, 0, _runtime_error, ())
        for i in range(8):
            scheduler.add(1, 0, time.sleep, (3,))
        scheduler.run()


if __name__ == '__main__':
    logging.basicConfig(
        format='[d2lbook:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s'
    )
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()
