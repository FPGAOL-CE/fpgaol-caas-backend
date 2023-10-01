import os
import time
import subprocess
import logging
logging.basicConfig(
    format='%(asctime)s line:%(lineno)s,  %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

compiler_timeout = 600
caasw_exec = "caas-wizard/caasw.py"

def compile(job):
    logger.info('\n Start compiling with simple=%s, %s, %s',
                job.jobs_dir, job.id, job.filename)
    work_root = os.path.join(job.jobs_dir, str(job.id))

    # Unzip the zipfile if there is one
    # Otherwise, it's website uploaded with .caas.conf in the file list
    hasZip = 0
    for z in job.filename:
        if '.zip' in z:
            try:
                with zipfile.ZipFile(z, 'r') as zip_ref:
                    zip_ref.extractall(work_root)
                hasZip = 1
            except zipfile.BadZipFile:
                print('BadZipFile!')
                return -1

    # Run caasw for Makefile gen: we don't trust user input
    ret = subprocess.call([caasw_exec, "mfgen", ".caas.conf", ".", "--overwrite"], cwd=work_root)
    if ret != 0:
        print('Error generating Makefile from project!')
        return -1

    # Run compilation within the unzipped directory
    # Just a reminder here: 
    #  API uploaded jobs:
    #   run.sh and Makefile are already prepared by caasw before uploading, 
    #   But we still run caasw mfgen on server again
    #   run.sh runs make in the corresponding Docker container
    #  Website submitted jobs: 
    #   .caas.conf is uploaded via frontend as well
    #   mfgen is run for the first time on server
    try:
        output = subprocess.check_output(["run.sh"], cwd=work_root, stderr=subprocess.STDOUT, timeout=compiler_timeout)
        print(output)
        return 0
    except subprocess.CalledProcessError as cpe:
        print('CalledProcessError!')
        return cpe.returncode
    except subprocess.TimeoutExpired:
        print('TimeoutExpired!')
        return -1
