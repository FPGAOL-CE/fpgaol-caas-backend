import os
import tornado

import logging
import time
import aiofiles

from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
from tornado.web import StaticFileHandler

from jobmanager import jobManager
from jobmanager import JOBS_DIR
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
        try:
            if token != open("token", "r").read()[:-1]:
                self.write("<p>Unauthorized Access</p>")
                return 
        except Exception as e:
            self.write("<p>Token file not found!</p>")
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

class FeedbackHandler(RequestHandler):
    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        body_arguments = self.request.body_arguments
        # print(body_arguments.keys())

        try:
            content = bytes.decode(body_arguments['fbContent'][0], encoding='utf-8')
        except KeyError:
            content = 'null'
        try:
            contact = bytes.decode(body_arguments['fbContact'][0], encoding='utf-8')
        except KeyError:
            contact = 'nobody'

        with open(time.strftime("feedbacks/%Y-%m-%d-%H-%M-%S", time.localtime()), "a") as f:
            f.write(contact + '\n' + content + '\n')

        data = {"code": 0,"msg": "done"}
        self.write(data)
        return

class SubmitHandler(RequestHandler):
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
            id = None 

        jobfiles = []

        ZipFileName = 'job.zip'
        inputZipFile = self.request.files.get('inputZipFile')
        if inputZipFile:
            jobfiles.append([ZipFileName, inputZipFile])

        XdcFileName = 'top.xdc'
        SrcFileName = 'top.v'
        ConfFileName = '.caas.conf'
        try:
            inputXdcFile = bytes.decode(
                body_arguments['inputXdcFile'][0], encoding='utf-8')
            jobfiles.append([XdcFileName, inputXdcFile])
        except KeyError:
            inputXdcFile = None
        try:
            inputSrcFile = bytes.decode(
                body_arguments['inputSrcFile'][0], encoding='utf-8')
            jobfiles.append([SrcFileName, inputSrcFile])
        except KeyError:
            inputSrcFile = None
        try:
            inputConfFile = bytes.decode(
                body_arguments['inputConfFile'][0], encoding='utf-8')
            jobfiles.append([ConfFileName, inputConfFile])
        except KeyError:
            inputConfFile = None

        try:
            inputNoSource = bytes.decode(
                body_arguments['inputNoSource'][0], encoding='utf-8')
            print('---' + inputNoSource)
            if inputNoSource != '1':
                inputNoSource = None
        except KeyError:
            inputNoSource = None

        success = 0
        msg = "Unable to submit"
        if id and inputZipFile:
            success = 1
            msg = "Request is ZIP. Compilation submitted... "
        elif id and inputXdcFile and inputSrcFile and inputConfFile:
            success = 1 
            msg = "Request is Source + Conf. Compilation submitted... "
        elif id and inputNoSource and inputConfFile:
            success = 1 
            msg = "Request is Conf without Source. Compilation submitted... "
        else:
            msg = "Neither ZIP or Source compilation can be satisfied"
            if not id:
                msg += ", id invalid"
            if not inputXdcFile:
                msg += ", input constraints(XDC) invalid"
            if not inputSrcFile:
                msg += ", input Verilog source code invalid"
            if not inputConfFile:
                msg += ", input Conf file (frontend-managed) invalid"
            if not inputZipFile:
                msg += ", input ZIP file (caasw submission) invalid"
            logger.info("\nJob id %s failed to submit!" % id)

        if (success == 1):
            jm.add_a_job(id, jobfiles)

        data = {"code": success,"msg": msg}
        self.write(data)
        return

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

        # if the job's not stale, we download with friendly info in filename
        running_jobs_temp, pending_jobs_temp, finished_jobs_temp, old_jobids = jm.list_jobs()
        submit_time = 'unknown'
        topname = 'unknown'
        for each in finished_jobs_temp:
            if id == each[0]:
                submit_time = each[1][:-9]
                topname = each[7]
        file = 'file-not-found'
        filename = 'invalid-file-name'
        if (filetype == 'bitstream'):
            for ext in ['bit', 'fs']:
                file = os.path.join(JOBS_DIR, '%s/build/top.%s' % (id, ext))
                filename = '%s-%s-%s.%s' % (id, topname, submit_time, ext)
                if os.path.exists(file):
                    break
        elif (filetype == 'log'):
            file = os.path.join(JOBS_DIR, "%s/build/top.log" % id)
            filename = '%s-%s-%s.log' % (id, topname, submit_time)
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
                # flush method call is import, it makes low memory occupy,
                # beacuse it send it out timely
                self.flush()

application = tornado.web.Application([
    (r'/submit', SubmitHandler),
    (r'/feedback', FeedbackHandler),
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

