import os
import queue
import logging
import threading
import shutil

import time
import base64

from compile import compile_new
from LogExtract import LogEx

JOBS_DIR = 'jobs'

logging.basicConfig(
    format='%(asctime)s line:%(lineno)s,  %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def try_compile(job, callback):
    try:
        compile_new(job)
    except Exception as e:
        logger.warning('try_compile: job %s got exception %s!' % (str(job.id), str(e)))
    callback(job.id)


class job:
    def __init__(self, id, sourcecode, device, jobs_dir = JOBS_DIR, simple=0):
        self.id = id
        self.submit_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.start_time = '-'
        self.finish_time = '-'
        self.device = device
        self.simple = simple
        self.jobs_dir = jobs_dir
        # self._create(id, sourcecode)

        try:
            if os.path.exists(os.path.join(self.jobs_dir, id)):
                shutil.rmtree(os.path.join(self.jobs_dir, id))
            os.mkdir(os.path.join(self.jobs_dir, id))
        except FileExistsError:
            logger.warning('job _create: dir (%s) exists, not a big deal. ' % id)

        self.filenames = []

        for filename, code in sourcecode:
            try:
                f = open(os.path.join(self.jobs_dir, id, filename), 'w')
                # ZIP file remains as is, and then unzipped by compiling functions
                # ZipFileName = 'UserZip.zip'
                # if filename == ZipFileName:
                    # #b64_content = base64.urlsafe_b64decode(code)
                    # f.write(code)
                # else:
                f.write(code)
                f.close()
                self.filenames.append(filename)
            except Exception as e:
                logger.warning(
                    'writing sourcecode file (%s) error, value:' % filename, e)
    # def _create(self, id, sourcecode):


class jobManager:

    def __init__(self, running_job_max, pending_jobs_max):
        self.running_job_max = running_job_max
        self.running_jobs = dict()
        self.pending_job_max = pending_jobs_max
        self.pending_jobs = queue.Queue(pending_jobs_max)
        self.using_job_id = set()
        self.finished_jobs = []
        self.old_jobs = os.listdir(JOBS_DIR)

        self.lock = threading.Lock()

    # simple=1: bare single text file and xdc file
    # simple=0: zip file for direct compilation
    def add_a_job(self, id, sourcecode, device, simple=0):
        if id in self.using_job_id:
            logger.warning('add_a_job: id %s in use!' % id)
            return
        self.using_job_id.add(id)
        a_new_job = job(id, sourcecode, device, simple=simple)
        self.lock.acquire()
        if len(self.running_jobs) < self.running_job_max:
            self.run_a_job(id, a_new_job)
        else:
            self.pend_a_job(id, a_new_job)
        self.lock.release()

    def job_finish(self, id):
        logger.info('\njob_finish: %s finished. ' % id)
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
                         job.start_time, job.finish_time])

        self.lock.release()
        return ret1, ret2, ret3, self.old_jobs
