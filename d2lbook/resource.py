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
import getpass

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
                           'device(\'/GPU:0\')', 'try_gpu()', 'try_gpu(0)', 'gpus=1')
    all_gpus_patterns = ('gpu(1)', 'device(\'cuda:1\')', 'device(\'/GPU:1\')',
                         'try_all_gpus', 'try_gpu(1)', 'gpus=2',
                         'gpus=3', 'gpus=4')
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
    description: str
    process: Optional[Any] = None
    locks: Sequence[int] = dataclasses.field(default_factory=list)
    done: bool = False
    start_time: datetime.datetime = datetime.datetime.now()
    end_time: Optional[datetime.datetime] = None

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

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

class Scheduler():
    """A schedule run multiple jobs in parallel under the resource constraint."""
    def __init__(self, num_cpu_workers, num_gpu_workers):
        self._num_cpus = num_cpu_workers
        self._num_gpus = num_gpu_workers
        self._locks = [False] * (self._num_cpus + self._num_gpus)
        user = getpass.getuser()
        self._inter_locks = [
            fasteners.InterProcessLock(f'/tmp/d2lbook_{user}_cpu_{i}')
            for i in range(self._num_cpus)] + [
                fasteners.InterProcessLock(f'/tmp/d2lbook_{user}_gpu_{i}')
                for i in range(self._num_gpus)]
        self._tasks = []
        self._failed_tasks = []
        self._start_job_lock = fasteners.InterProcessLock(
            f'/tmp/d2lbook_{user}_start_job')

    def add(self, num_cpus, num_gpus, target, args, description=''):
        """Add tasks into the queue."""
        assert not (num_cpus == 0 and num_gpus == 0), \
                'Need at least one CPU or GPU'
        assert num_cpus <= self._num_cpus and num_gpus <= self._num_gpus, \
            f'Not enough resources (CPU {self._num_cpus}, GPU {self._num_gpus} ) to run the task (CPU {num_cpus}, GPU {num_gpus})'

        if not description:
            description = f'Target {target} with args {args}'
        self._tasks.append(_Task(num_cpus, num_gpus, target, args,
                                 description))

    @property
    def failed_tasks(self):
        return [(task.description, err, trace)
                for task, err, trace in self._failed_tasks]

    @property
    def error_message(self):
        if not self.failed_tasks:
            return ''
        errors = [
            f'{len(self.failed_tasks)} notebooks are failed to evaluate:']
        for task, err, trace in self.failed_tasks:
            errors += [f'Task {task} exited with error: {err}', trace]
        return '\n\n'.join(errors)

    def run(self):
        """Run the tasks and block until they are done."""
        def _device_info(task):
            cpus = task.locks[:task.num_cpus]
            gpus = [i - self._num_cpus for i in task.locks[task.num_cpus:]]
            info = []
            if cpus: info.append(f'CPU {cpus}')
            if gpus: info.append(f'GPU {gpus}')
            return ', '.join(info)

        def _runtime(task):
            end_time = task.end_time if task.end_time else datetime.datetime.now(
            )
            return utils.get_time_diff(task.start_time, end_time)

        def _summary_heavy_tasks():
            if self._tasks:
                logging.info(
                    f'All {len(self._tasks)} tasks are done, sorting by runtime:'
                )
                self._tasks.sort(
                    key=lambda task: (task.end_time - task.start_time).seconds)
                for task in self._tasks:
                    logging.info(
                        f'  - {_runtime(task)} on {_device_info(task)} for {task.description}'
                    )

        def _status():
            num_done, num_not_started, num_running = 0, 0, 0
            for task in self._tasks:
                if task.done: num_done += 1
                if task.process: num_running += 1
                if not task.process and not task.done: num_not_started += 1

            logging.info(
                f'  Status: {num_running} running tasks, {num_done} done, {num_not_started} not started'
            )
            for task in self._tasks:
                if task.process:
                    logging.info(
                        f'    - Task "{task.description}" on {_device_info(task)} is running for {_runtime(task)}'
                    )

        # try large gpu workloads first
        self._tasks.sort(reverse=True, key=lambda task:
                         (task.num_gpus, task.num_cpus))

        last_status_t = 0
        for t in range(24 * 60 * 60):  # run at most 24 hours
            if all([task.done for task in self._tasks]):
                break

            if t > last_status_t + 60:
                last_status_t = t
                _status()

            for task in self._tasks:
                if task.process or task.done:
                    continue
                locks = self._lock(0, self._num_cpus, task.num_cpus) + \
                        self._lock(self._num_cpus, self._num_cpus+self._num_gpus, task.num_gpus)
                if len(locks) < task.num_cpus + task.num_gpus:
                    self._unlock(locks)
                    continue
                task.locks = locks
                # a brutal fix to https://github.com/jupyter/nbconvert/issues/1066
                # if two ci jobs start to eval notebook at the same time, it may
                # cause the port bind conflict. here i require the ci job to acquire
                # a global lock for 1 sec.
                self._start_job_lock.acquire()
                message = f'Starting task "{task.description}" on {_device_info(task)}'
                logging.info(message)
                task.start_time = datetime.datetime.now()
                gpus = [i - self._num_cpus for i in locks[task.num_cpus:]]
                task.process = Process(target=_target,
                                       args=(gpus, task.target, *task.args))
                task.process.start()
                _status()
                last_status_t = t
                time.sleep(1)
                self._start_job_lock.release()
                break

            # check if any one is finished
            for task in self._tasks:
                if task.done or not task.process: continue
                if not task.process.is_alive():
                    for lock in task.locks:
                        self._locks[lock] = False
                        self._inter_locks[lock].release()
                    task.end_time = datetime.datetime.now()
                    if task.process.exception:
                        error, traceback = task.process.exception
                        self._failed_tasks.append((task, error, traceback))
                        logging.error(
                            f'Task "{task.description}" on {_device_info(task)} exited with error: {error}\n{traceback}'
                        )
                    else:
                        logging.info(
                            f'Task "{task.description}" on {_device_info(task)} is finished in {_runtime(task)}'
                        )
                    task.process = None
                    task.done = True

            time.sleep(1)

        _summary_heavy_tasks()

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
        return locks

    def _unlock(self, locks):
        for i in locks:
            self._inter_locks[i].release()
            self._locks[i] = False

def _target(gpus, target, *args):
    if not gpus:
        # it will triggler an runtime error if target actually uses a gpu
        gpus = [""]
    os.environ['CUDA_VISIBLE_DEVICES'] = ','.join([str(g) for g in gpus])
    return target(*args)
