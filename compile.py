import os
import time
import subprocess
import logging
import zipfile
logging.basicConfig(
    format='%(asctime)s line:%(lineno)s,  %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

compiler_timeout = 240
caasw_exec = os.path.join(os.getcwd(), "caas-wizard/caasw.py")

def try_compile(job, callback):
    returnval = -100
    try:
        returnval = compile(job)
    except Exception as e:
        logger.warning('try_compile: job %s got exception %s!' % (str(job.id), str(e)))
    job.succeeded = returnval == 0
    job.timeouted = returnval == -1
    job.killed = returnval == 233
    callback(job.id)

def compile(job):
    logger.info('\n Start compiling with %s, %s, %s',
                job.jobs_dir, job.id, job.filenames)
    work_root = os.path.join(job.jobs_dir, str(job.id))
    os.mkdir(os.path.join(work_root, 'build'))

    # Unzip the zipfile if there is one
    # Otherwise, it's website uploaded with .caas.conf in the file list
    hasZip = 0
    for z in job.filenames:
        if '.zip' in z:
            try:
                with zipfile.ZipFile(os.path.join(work_root, z), 'r') as zip_ref:
                    zip_ref.extractall(work_root)
                hasZip = 1
            except zipfile.BadZipFile:
                print('BadZipFile!')
                return -1

    # Run caasw for Makefile gen: we don't let user upload Makefile
    # Redirect output to build/top.log, so even if this fails (especially with Giturl),
    # user still get a log to read
    ret = -1
    with open(os.path.join(work_root, "build", "top.log"), "w") as logf:
        ret = subprocess.call([caasw_exec, "mfgen", ".caas.conf", ".", "--overwrite", "--clone",
                               "--compile" if job.tasktype == 'compile' else "--sim"],
                               cwd=work_root, stdout=logf, stderr=logf)
    if ret != 0:
        print('Error generating Makefile from project!')
        return -1

    # Run compilation within the unzipped directory
    # Just a reminder here: 
    #  API uploaded jobs:
    #   run_caas.sh and Makefile are already prepared by caasw before uploading, 
    #   But we still run caasw mfgen on server again
    #   run_caas.sh runs make in the corresponding Docker container
    #  Website submitted jobs: 
    #   .caas.conf is uploaded via frontend as well
    #   mfgen is run for the first time on server
    try:
        ret = subprocess.run([os.path.join(os.getcwd(), job.jobs_dir, job.id,
                                           "run_caas.sh" if job.tasktype == 'compile' else "run_sim.sh")],
                                           cwd=work_root, timeout=compiler_timeout)
        return ret.returncode
    except subprocess.CalledProcessError as cpe:
        print('CalledProcessError!')
        return cpe.returncode
    except subprocess.TimeoutExpired:
        print('TimeoutExpired!')
        return -1
