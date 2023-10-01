import os
import queue
import logging
import threading
import shutil

import time
import base64

from compile import try_compile, compile
from LogExtract import LogEx

JOBS_DIR = 'jobs'

logging.basicConfig(
    format='%(asctime)s line:%(lineno)s,  %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class job:
    def __init__(self, id, sourcecode, jobs_dir = JOBS_DIR):
        self.id = id
        self.submit_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.start_time = '-'
        self.finish_time = '-'
        self.jobs_dir = jobs_dir
        self.succeeded = 0
        self.timeouted = 0
        self.killed = 0

        try:
            if os.path.exists(os.path.join(self.jobs_dir, id)):
                shutil.rmtree(os.path.join(self.jobs_dir, id))
            os.mkdir(os.path.join(self.jobs_dir, id))
        except FileExistsError:
            logger.warning('job _create: dir (%s) exists, not a big deal. ' % id)

        self.filenames = []

        for filename, code in sourcecode:
            try:
                f = open(os.path.join(self.jobs_dir, id, filename), 
                         'wb' if '.zip' in filename else 'w')
                f.write(code)
                f.close()
                self.filenames.append(filename)
            except Exception as e:
                logger.warning(
                    'writing sourcecode file (%s) error, value:' % filename, e)

class jobManager:
    def __init__(self, running_job_max, pending_jobs_max):
        self.running_job_max = running_job_max
        self.running_jobs = dict()
        self.pending_job_max = pending_jobs_max
        self.pending_jobs = queue.Queue(pending_jobs_max)
        self.using_job_id = set()
        self.finished_jobs = []
        if not os.path.exists(JOBS_DIR):
           os.makedirs(JOBS_DIR)
        # this is kinda strange...
        self.old_jobs = os.listdir(JOBS_DIR)
        self.lock = threading.Lock()

    def add_a_job(self, id, sourcecode):
        if id in self.using_job_id:
            logger.warning('add_a_job: id %s in use!' % id)
            return
        self.using_job_id.add(id)
        a_new_job = job(id, sourcecode)
        self.lock.acquire()
        # remove finished job with same id
        # low efficiency may be
        for j in self.finished_jobs:
            if j.id == id:
                self.finished_jobs.remove(j)
                del j
        if len(self.running_jobs) < self.running_job_max:
            self.run_a_job(id, a_new_job)
        else:
            self.pend_a_job(id, a_new_job)
        self.lock.release()

    def job_finish(self, id):
        logger.info('\njob_finish: %s finished, %s. ' % (id, 'succeeded' if self.running_jobs[id].succeeded else 'failed'))
        # LogEx(id)
        self.lock.acquire()
        self.running_jobs[id].finish_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime())
        self.finished_jobs.append(self.running_jobs[id])
        del self.running_jobs[id]
        self.using_job_id.remove(id)
        if not self.pending_jobs.empty():
            job = self.pending_jobs.get()
            self.run_a_job(job.id, job)
        self.lock.release()

    def pend_a_job(self, id, job):
        self.pending_jobs.put(job)

    def run_a_job(self, id, job):
        self.running_jobs[id] = job
        job.start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        threading.Thread(target=try_compile, args=(job, self.job_finish)).start()

    def list_jobs(self):
        ret1 = []
        ret2 = []
        ret3 = []
        self.lock.acquire()
        for id in self.running_jobs:
            job = self.running_jobs[id]
            ret1.append([id, job.submit_time,
                         job.start_time, job.finish_time])
        for job in self.pending_jobs.queue:
            ret2.append([job.id, job.submit_time,
                         job.start_time, job.finish_time])

        for job in self.finished_jobs:
            ret3.append([job.id, job.submit_time,
                         job.start_time, job.finish_time, job.succeeded, job.timeouted, job.killed, 'top'])

        self.lock.release()
        return ret1, ret2, ret3, self.old_jobs
