"""Manage compute resources
"""
import dataclasses
import datetime
import logging
import multiprocessing as mp
import os
import random
import subprocess
import threading
import time
import traceback
from typing import Any, Optional, Sequence

import fasteners

from d2lbook import utils

def get_available_gpus():
    """Return a list of available GPUs with their names"""
    cmd = 'nvidia-smi --query-gpu=name --format=csv,noheader'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, _ = process.communicate()
    if process.returncode == 0:
        return stdout.decode().splitlines()
    return []

def get_notebook_gpus(notebook, max_gpus):
    """Return the # of GPUs needed for a notebook."""
    # several heuristics, not necessary accurate
    # TODO(mli) support a special mark in notebook to hint the #gpus
    single_gpu_patterns = ('gpu()', 'gpu(0)', 'device(\'cuda\')',
                           'device(\'/GPU:0\')', 'try_gpu()', 'try_gpu(0)')
    all_gpus_patterns = ('gpu(1)', 'device(\'cuda:1\')', 'device(\'/GPU:1\')',
                         'try_all_gpus', 'try_gpu(1)')
    n_gpus = 0
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            if any([p in cell.source for p in single_gpu_patterns]):
                n_gpus = max(n_gpus, 1)
            if any([p in cell.source for p in all_gpus_patterns]):
                n_gpus = max(n_gpus, max_gpus)
    return n_gpus

@dataclasses.dataclass
class _Task():
    num_cpus: int
    num_gpus: int
    target: Any
    args: Sequence[Any]
    message: str
    process: Optional[Any] = None
    locks: Sequence[int] = dataclasses.field(default_factory=list)
    done: bool = False
    start_time: datetime.datetime = datetime.datetime.now()

class Process(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still rise this exception if you need to

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

class Scheduler():
    """A schedule run multiple jobs in parallel under the resource constraint."""
    def __init__(self, num_cpu_workers, num_gpu_workers=-1):
        self._num_cpus = num_cpu_workers
        self._num_gpus = len(get_available_gpus())
        if num_gpu_workers >= 0 and self._num_gpus < num_gpu_workers:
            raise ValueError(
                f'# of available GPUs {self._num_gpus} is less than requested {num_gpu_workers}'
            )
        self._locks = [False] * (self._num_cpus + self._num_gpus)
        self._inter_locks = [
            fasteners.InterProcessLock(f'/tmp/d2lbook_cpu_{i}')
            for i in range(self._num_cpus)] + [
                fasteners.InterProcessLock(f'/tmp/d2lbook_gpu_{i}')
                for i in range(self._num_gpus)]
        self._tasks = []
        self._failed_jobs = []

    def add(self, num_cpus, num_gpus, target, args, message=''):
        """Add tasks into the queue."""
        if num_cpus == 0 and num_gpus == 0:
            raise ValueError('Need at least one CPU or GPU')
        if num_cpus > self._num_cpus or num_gpus > self._num_gpus:
            raise ValueError('Not enough resources to run the task')
        self._tasks.append(_Task(num_cpus, num_gpus, target, args, message))

    @property
    def failed_jobs(self):
        return self._failed_jobs

    def run(self):
        """Run the tasks and block until they are done."""
        def _target(gpus, target, *args):
            if gpus:
                os.environ['CUDA_VISIBLE_DEVICES'] = ','.join([
                    str(g) for g in gpus])
            return target(*args)

        while True:
            for i, task in enumerate(self._tasks):
                if task.process or task.done:
                    continue
                locks = self._lock(0, self._num_cpus, task.num_cpus) + \
                        self._lock(self._num_cpus, self._num_cpus+self._num_gpus, task.num_gpus)
                cpus = locks[:task.num_cpus]
                gpus = [i - self._num_cpus for i in locks[task.num_cpus:]]
                if locks:
                    message = f'Starting task {i} on '
                    if cpus:
                        message += f'CPU {cpus} '
                    if gpus:
                        message += f'GPU {gpus} '
                    if task.message:
                        message += task.message
                    else:
                        message += f'for target {task.target} with args {task.args}'
                    logging.info(message)
                    task.locks = locks
                    task.start_time = datetime.datetime.now()
                    task.process = Process(
                        target=_target, args=(gpus, task.target, *task.args))
                    task.process.start()
                    break

            # check if any one is finished
            for i, task in enumerate(self._tasks):
                if task.done or not task.process: continue
                if not task.process.is_alive():
                    for lock in task.locks:
                        self._locks[lock] = False
                        self._inter_locks[lock].release()
                    if task.process.exception:
                        error, traceback = task.process.exception
                        self._failed_jobs.append(i)
                        logging.error(
                            f'Task {i} exited with error: {error}\n{traceback}'
                        )
                    task.process = None
                    task.done = True
                    runtime = utils.get_time_diff(task.start_time,
                                                  datetime.datetime.now())
                    logging.info(f'Task {i} is finished in {runtime}')

            # check if all done
            if all([task.done for task in self._tasks]):
                return

            time.sleep(1)

    def _lock(self, start, end, n):
        ids = list(range(start, end))
        random.shuffle(ids)
        locks = []
        for i in ids:
            if len(locks) >= n:
                break
            if self._inter_locks[i].acquire(
                    blocking=False) and not self._locks[i]:
                self._locks[i] = True
                locks.append(i)
        if len(locks) >= n:
            return locks
        for i in locks:
            self._inter_locks[i].release()
            self._locks[i] = False
        return []
