import os
# from edalize import get_edatool
import time

import logging
logging.basicConfig(
    format='%(asctime)s line:%(lineno)s,  %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

f4pga_docker_spawner = 'f4pga_tools/f4pga.sh'
#vivado_exec = '/opt/Xilinx/Vivado/2020.2/bin/vivado'
vivado_exec = '/tools/Xilinx/Vivado/2019.2/bin/vivado'
vivado_tools_dir = 'vivado_tools'
vivado_ip_dir = 'vivado_tools/ip'
tcl_build = 'build.tcl'
# vivado_mode = 'tcl'
vivado_mode = 'batch'


# def compile(jobdir, id, filenames, device):
    # print(jobdir, id, filenames, device)
    # tcl_build_path = os.path.join(os.getcwd(), vivado_tools_dir, tcl_build)
    # ip_dir = os.path.join(os.getcwd(), vivado_ip_dir)
    # work_root = os.path.join(jobdir, id)
    # os.system('unzip -o ' + work_root + '/' + filenames[0] + ' -d ' + work_root)

    # os.system(vivado_exec + ' -mode ' + vivado_mode + ' -source ' + tcl_build_path + 
            # ' -tclargs ' + work_root + ' ' + device + ' ' + ip_dir)

def compile_new(job):
    logger.info('\n Start compiling with simple=%s, %s, %s, %s, %s',
                job.simple, job.jobs_dir, job.id, job.filenames, job.device)

    work_root = os.path.join(job.jobs_dir, str(job.id))
    command = f4pga_docker_spawner + ' ' + work_root + ' ' + str(job.simple) + ' ' + job.device + ' ' + job.filenames[0] + ' ' + job.filenames[1]
    print(command)
    return os.system(command)
    # tcl_build_path = os.path.join(os.getcwd(), vivado_tools_dir, tcl_build)
    # ip_dir = os.path.join(os.getcwd(), vivado_ip_dir)
    # os.system('unzip -o ' + work_root + '/' + filenames[0] + ' -d ' + work_root)

    # os.system(vivado_exec + ' -mode ' + vivado_mode + ' -source ' + tcl_build_path + 
            # ' -tclargs ' + work_root + ' ' + device + ' ' + ip_dir)
