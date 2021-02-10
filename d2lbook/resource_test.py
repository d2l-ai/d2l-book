"""
Run multiple instances from terminal to test

python d2lbook/resource_test.py
"""
from d2lbook import resource
import unittest
import time
import logging
import os

def _incorrect_code():
    for i in a:
        print(i)

def _runtime_error():
    return 1 / 0

class TestResource(unittest.TestCase):
    def test_get_available_gpus(self):
        self.assertGreaterEqual(len(resource.get_available_gpus()), 0)

    def test_gpus(self):
        def _job():
            self.assertEqual(len(os.environ['CUDA_VISIBLE_DEVICES']), 1)
            time.sleep(1)

        scheduler = resource.Scheduler(num_cpu_workers=2, num_gpu_workers=2)
        scheduler.add(1, 1, _job, ())
        scheduler.add(1, 1, _job, ())
        scheduler.run()

    def test_scheduler(self):
        scheduler = resource.Scheduler(num_cpu_workers=2, num_gpu_workers=2)
        for _ in range(3):
            scheduler.add(1, 0, time.sleep, (2,))
        scheduler.add(1, 1, _incorrect_code, ())
        scheduler.add(1, 2, _runtime_error, ())
        scheduler.run()
        self.assertEqual(len(scheduler.failed_tasks), 2)
        logging.info(scheduler.error_message)

if __name__ == '__main__':
    logging.basicConfig(
        format='[d2lbook:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s'
    )
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()
