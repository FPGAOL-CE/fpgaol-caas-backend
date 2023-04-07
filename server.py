import os
import tornado

import logging
import time
import aiofiles

from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
from tornado.web import StaticFileHandler

from jobmanager import jobManager
# from FileExist import FilesEx
import json

jm = jobManager(8, 64)

logging.basicConfig(
    format='%(asctime)s line:%(lineno)s,  %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class MainHandler(RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.render('page/index.html')

class aboutHandler(RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.render('page/about.html')

class jobsHandler(RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        token = self.get_argument('token', None, True)
        if token != open("token", "r").read()[:-1]:
            self.write("<p>Unauthorized Access</p>")
            return 

        running_jobs, pending_jobs, finished_jobs, old_jobids = jm.list_jobs()
        
        # self.render('page/jobs.html', running_jobs=running_jobs, pending_jobs=pending_jobs, finished_jobs=finished_jobs)
        self.write('running_jobs:\n' + str(running_jobs) + '\npending_jobs:\n' + str(pending_jobs) +
                  '\nfinished_jobs:\n' + str(finished_jobs) + 'old_jobs:\n' + str(old_jobids) + '\n')

class StatusHandler(RequestHandler):
    def get(self,id):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        running_jobs_temp, pending_jobs_temp, finished_jobs_temp, old_jobids = jm.list_jobs()
        
        # feels inefficient...
        # running_jobs = []
        # pending_jobs = []
        # finished_jobs = []
        for each in running_jobs_temp:
            if id == each[0]:
                self.write('running')
            # running_jobs.append(each[0])

        for each in pending_jobs_temp:
            if id == each[0]:
                self.write('pending')
            # pending_jobs.append(each[0])

        for each in finished_jobs_temp:
            if id == each[0]:
                self.write('finished.%s%s%s' % 
                           ('succeeded' if each[4] else 'failed',
                            '.timeout' if each[5] else '', 
                            '.outofmemory' if each[6] else ''))
            # finished_jobs.append(each[0])

        # if id in running_jobs:
        # elif id in pending_jobs:
            # self.write('pending')
        # elif id in finished_jobs or id in old_jobids:
            # self.write('finished.%s' % 'succeeded' if )
        # else:
            # self.write('error')

class InteractiveSubmitHandler(RequestHandler):
    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        body_arguments = self.request.body_arguments
        # print(body_arguments.keys())

        try:
            id = bytes.decode(body_arguments['inputJobId'][0], encoding='utf-8')
            logger.info("\nNew submit: id %s" % id)
        except KeyError:
            id = 0

        try:
            inputFpgaPart = bytes.decode(
                body_arguments['inputFpgaPart'][0], encoding='utf-8')
        except KeyError:
            inputFpgaPart = 0

        XdcFileName = 'top.xdc'
        SrcFileName1 = 'top.v'

        #XdcFileName = bytes.decode(
            #body_arguments['XdcFileName'][0], encoding='utf-8')
        try:
            inputXdcFile = bytes.decode(
                body_arguments['inputXdcFile'][0], encoding='utf-8')
        except KeyError:
            inputXdcFile = 0

        # SrcFileName1 = bytes.decode(
            # body_arguments['SrcFileName1'][0], encoding='utf-8')
        try:
            inputSrcFile1 = bytes.decode(
                body_arguments['inputSrcFile1'][0], encoding='utf-8')
        except KeyError:
            inputSrcFile1 = 0

  #      SrcFileName2 = bytes.decode(
  #          body_arguments['SrcFileName2'][0], encoding='utf-8')
  #      inputFile2 = bytes.decode(
  #          body_arguments['inputFile2'][0], encoding='utf-8')

        #inputFiles = body_arguments['inputFile1']
        # SrcFileName = body_arguments['SrcFilname']
        #print(id, XdcFileName, SrcFileName1, SrcFileName2, inputFPGA)
        sourcecode = [[XdcFileName, inputXdcFile], [SrcFileName1, inputSrcFile1]]

        # sourcecode = [[inputXdcFile, inputSrcFile1]]

        # if SrcFileName2:
            # sourcecode.append([SrcFileName2, inputFile2])

        # for i,inputFile in enumerate(inputFiles):
            # sourcecode.append([str(i)+'.v',bytes.decode(inputFile,encoding='utf-8')])

  #      print(sourcecode)
        # if  id and inputFPGA and XdcFileName and inputXdcFile and inputFiles:

        returncode = 0
        msg = "Unable to submit"

        if id and inputFpgaPart and inputXdcFile and inputSrcFile1:
            returncode = 1 
            msg = "Compilation submitted... "
        else:
            if not id:
                msg += ", id invalid"
            if not inputFpgaPart:
                msg += ", input FPGA Part invalid"
            if not inputXdcFile:
                msg += ", input constraints(XDC) invalid"
            if not inputSrcFile1:
                msg += ", input Verilog source code invalid"
            logger.info("\nJob id %s failed to submit!" % id)

        if (returncode == 1):
            jm.add_a_job(id, sourcecode, inputFpgaPart, simple=1)

        data = {"code": returncode,"msg": msg}
        self.write(data)
        return
        # self.write(data)
        # self.write("<h1>Results</h1>")
        # time.sleep(1)
        # self.write("<p>11111</p>")
        # await tornado.ioloop.IOLoop.current().run_in_executor(None, self.do_compiling, (id, sourcecode, inputFpgaPart))

        # self.redirect('/jobs')

    # # at this stage, we have all required files and params
    # def do_compiling(self, id, sourcecode, devicepart):
        # time.sleep(10)
        # pass

    # def on_connection_close(self):
        # pass

# class OldSubmitHandler(RequestHandler):
    # def post(self):
        # self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        # self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        # code = 0
        # msg = "提交编译失败"
        # body_arguments = self.request.body_arguments
        # # print(body_arguments.keys())
        # id = bytes.decode(body_arguments['inputJobId'][0], encoding='utf-8')
        # logger.info("\nCompilingPrjid%s"%id)
        # inputFPGA = bytes.decode(
            # body_arguments['inputFPGA'][0], encoding='utf-8')
        # #XdcFileName = bytes.decode(
            # #body_arguments['XdcFileName'][0], encoding='utf-8')
        # #inputXdcFile = bytes.decode(
            # #body_arguments['inputXdcFile'][0], encoding='utf-8')
        # ZipFileName = 'UserZip.zip'
        # XdcFileName = 'top.xdc'
        # SrcFileName1 = 'top.v'
        
        # inputZipFile = self.request.files['inputZipFile'][0].get('body')
  # #      SrcFileName1 = bytes.decode(
  # #          body_arguments['SrcFileName1'][0], encoding='utf-8')
  # #      inputFile1 = bytes.decode(
  # #          body_arguments['inputFile1'][0], encoding='utf-8')
  # #      SrcFileName2 = bytes.decode(
  # #          body_arguments['SrcFileName2'][0], encoding='utf-8')
  # #      inputFile2 = bytes.decode(
  # #          body_arguments['inputFile2'][0], encoding='utf-8')

        # #inputFiles = body_arguments['inputFile1']
        # # SrcFileName = body_arguments['SrcFilname']
        # #print(id, XdcFileName, SrcFileName1, SrcFileName2, inputFPGA)

        # # Our convention now: XDC file MUST be the first
        # sourcecode = [[XdcFileName, inputXdcFile], [SrcFileName1, inputSrcFile1]]

        # # sourcecode = [[ZipFileName, inputZipFile]]

        # # for i,inputFile in enumerate(inputFiles):
            # # sourcecode.append([str(i)+'.v',bytes.decode(inputFile,encoding='utf-8')])

  # #      print(sourcecode)
        # # if  id and inputFPGA and XdcFileName and inputXdcFile and inputFiles:
        # if  id and inputFPGA and inputZipFile:
            # code = 1 
            # msg = "提交编译成功，请使用查询接口查询编译状态"
        # else:
            # if not id:
                # msg += ",the id is not correct"
            # if not inputFPGA:
                # msg += ",the inputFPGA is not correct"
            # if not inputZipFile:
                # msg += ",the inputZipFile is not correct"
            # data = {"code": code,"msg": msg}
            # self.write(data)
            # logger.info("\nCompilingPrjid%sFinish"%id)
            # return 

        # # if SrcFileName2:
            # # sourcecode.append([SrcFileName2, inputFile2])
        # data = {"code": code,"msg": msg}
        # self.write(data)

        # jm.add_a_job(id, sourcecode, inputFPGA)
        # # self.redirect('/jobs')


# class QueryHandler(RequestHandler):
    # def get(self,id):
        # self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        # self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        # status = 0
        # code = 1
        # msg = ''
        # #output = dict()
        # running_jobs_temp, pending_jobs_temp, finished_jobs_temp, old_jobids = jm.list_jobs()

        # running_jobs = []
        # pending_jobs = []
        # finished_jobs = []
        # for each in running_jobs_temp:
            # running_jobs.append(each[0])

        # for each in pending_jobs_temp:
            # pending_jobs.append(each[0])

        # for each in finished_jobs_temp:
            # finished_jobs.append(each[0])
        # path = "./jobs/%s/results/top.bit"%id
        # file_exist = os.path.exists(path)
        # #print(jm.list_jobs())
        # if id in running_jobs:
            # status = 1
            # msg = 'running'
        # elif id in pending_jobs:
            # status = 2
            # msg = 'pending'
        # elif (id in finished_jobs or id in old_jobids) and file_exist:
            # status = 3
            # msg = 'successful'
        # elif (id in finished_jobs or id in old_jobids) and ~file_exist:
            # status = 4
            # with open("./jobs/%s/error.log"%id,'r') as f:
                # error = f.read()
            # msg = 'compiling failed, the error message is as follows:\n'+error
        # else:
            # msg = 'error'
            # status = 0

        # #output["msg"] = msg
        # #output["status"] = status
        # data = {"code": code,"msg": msg,"data":{"status": status}}
        # self.write(data)

# class JobListHandler(RequestHandler):
    # def get(self):
        # self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        # self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        # #output = dict()
        # running_jobs_temp, pending_jobs_temp, finished_jobs_temp, old_jobids = jm.list_jobs()

        # new_jobs = []
        # data = []
        # for each in running_jobs_temp:
            # data.append([each[0],1,each[1]])
            # new_jobs.append(each[0])

        # for each in pending_jobs_temp:
            # data.append([each[0],2,each[1]])
            # new_jobs.append(each[0])

        # for each in finished_jobs_temp:
            # path = "./jobs/%s/results/top.bit"%each[0]
            # file_exist = os.path.exists(path)
            # new_jobs.append(each[0])
            # if file_exist:
                # data.append([each[0],3,each[1]])
            # else:
                # data.append([each[0],4,each[1]])
            
        # for each in old_jobids:
            # if each not in new_jobs:
                # path = "./jobs/%s/results/top.bit"%each
                # file_exist = os.path.exists(path)
                # if file_exist:
                    # data.append([each,3,""])
                # else:
                    # data.append([each,4,""])
        # self.write({'data':data})

class DownloadHandler(RequestHandler):
    async def get(self, id, filetype):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        file = ''
        filename = ''
        if (filetype == 'bitstream'):
            file = "./jobs/%s/top.bit" % id
            filename = 'top-%s.bit' % id
        elif (filetype == 'log'):
            file = "./jobs/%s/top.log" % id
            filename = 'top-%s.log' % id
        else:
            self.write("Invalid file type requested!")
            return
        file_exist = os.path.exists(file)
        if not file_exist:
            self.write("<p>Requested %s not found for id %s!</p>" % (filetype, str(id)))
            return
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % filename)
        # the aiofiles use thread pool,not real asynchronous
        async with aiofiles.open(file, 'rb') as f:
            while True:
                data = await f.read(1024)
                if not data:
                    break
                self.write(data)
                # flush method call is import,it makes low memory occupy,beacuse it send it out timely
                self.flush()

    # def get(self,id):
        # self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        # self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        # self.set_header('Content-Type', 'application/octet-stream')
        # self.set_header('Content-Disposition', 'attachment; filename=top.bit')
        # # code = 1
        # # msg = "下载成功"
        # bitfile = "./jobs/%s/top.bit" % id
        # file_exist = os.path.exists(bitfile)
        # # File_list = FilesEx(id)
        # if file_exist:
            # self.write(open(bitfile, 'rb').read())
            # # data = {"code": code,"msg": msg,"data":File_list}
            # # self.write(data)
        # # else:
            # # code = 0
            # # msg = "下载失败，没有相应比特流文件"
            # # data = {"code": code,"msg": msg,"data":File_list}
            # # self.write(data)

application = tornado.web.Application([
    (r'/submit', InteractiveSubmitHandler),
    (r'/jobs', jobsHandler),
    (r'/about', aboutHandler),
    (r'/status/(\w+)',StatusHandler),
    # (r'/query/(\w+)',QueryHandler),
    (r'/download/(\w+)/(\w+)',DownloadHandler),
    # (r'/api_joblist', JobListHandler),
    (r"/", MainHandler),
    (r'/(.*)', StaticFileHandler, {'path': './page/'}),
    
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(18888)

    logger.info('Server started')
    tornado.ioloop.IOLoop.current().start()
