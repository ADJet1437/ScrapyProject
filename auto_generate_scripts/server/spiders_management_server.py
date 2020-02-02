# -*- coding: utf8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.template
import tornado.options
import tornado.autoreload
from tornado.wsgi import WSGIContainer
import os,json, csv, psutil, hashlib, commands
from datetime import datetime,timedelta
from time import sleep, strptime
from gen_spiders import *
from generator_template import *
from conf import *
from orm.alascrapy_spiders_elements import *
from apscheduler.schedulers.background import BackgroundScheduler
import sys, traceback

api_root = '/spm'


source_content_cache = {}    #{con_identification:{pid:{}, pro:{}, rev:{}}}, csv content exist up to 24 hours
source_content_cache_duration = 60 * 24 * 3

source_signal = {}
source_id_testing = {}  #make sure that 1 source can not be excuted twice at same time
scripts_path = ['/var/local/load/running/', '/var/local/load/finished/']
script_execution_duration = 5
#script_execution_duration = 15


class JSONHandler(tornado.web.RequestHandler):
    def get_error_html(self, status_code, **kwargs):
        msg = str(kwargs.get("exception", "unknown error"))
        self.write_json({"error": msg}, status_code=404)

    def write_json(self, data, status_code=200):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.set_status(status_code)
        self.write(json.dumps(data, indent=4, ensure_ascii=False))
        
    def write_error(self, status_code, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.set_status(status_code)
        self.write("Dear user! You caused a %d error." % status_code)

    def write_json_page(self, content, idx, page, rows):
        total = str(len(content))
        res_dict = {'total':total, 'rows':content}
        if int(page) * int(rows) < total:
            res_dict = {'total':total, 'rows':content[idx:int(page) * int(rows)]}
        else:
            res_dict = {'total':total, 'rows':content[idx:]}
        self.write_json(res_dict)
        

class LoadScriptHandler(JSONHandler):
    def post(self):
        content = self.request.body_arguments
        try:
            source_id = content['source_id'][0]
            json_file = os.path.join(generator_save_path, "sd%s.json" % source_id)
            data = ""

            with open(json_file, "r") as f:
                data = f.read()
            self.write_json({'success':True,'data':data})
        except:
            info = sys.exc_info()
            self.write_json({'success':False,'desc':"Script failed to load. %s : %s" % (info[0], info[1]) } , 500)

class SaveScriptHandler(JSONHandler):
    def post(self):
        content = self.request.body_arguments
        try:
            source_id = content['source_id'][0]
            data = content['data'][0]
            json_file = os.path.join(generator_save_path, "sd%s.json" % source_id)
        
            with open(json_file, "w") as f:
                f.write(data)
            self.write_json({'success':True, 'desc':"Script has been created!"}, 200)
        except :
            info = sys.exc_info()
            self.write_json({'success':False,'desc':"Script failed to save. %s : %s" % (info[0], info[1]) } , 500)
            




class GenSpiderHandler(JSONHandler):
    def post(self):
        value = [], []
        content = self.request.body_arguments
        for key in content:
            if 'script_name' in key:
                script_name = content[key]
            if 'source_id' in key:
                source_id = content[key]
            if 'value' in key:
                value = content[key]
        if value == ([], [], [])  or script_name == [''] or source_id == ['']:
            self.write_json("Dear user! Failed to generate a spider, please check the parameters you entered.", 200)
            self.finish()
            return
        
        try:
            sname = script_name[0].lower().replace('-', '_').replace('.py', '')
            generator_name = sname + '_generator.py'
            generator_fp = os.path.join(generator_save_path, generator_name)
            fh = open(generator_fp, 'w+')
            generator_import_code = generator_import()
            fh.write(generator_import_code)
            fh.write(generator_append)
            engine, session = get_session()
            update_spider_record(session, source_id[0], sname)
            spider_id = get_spider_id(session, sname)
            fn_temp = 'gen_init'
            pnames, pvalues = [], []
            vlen = len(value)
            for idx in xrange(vlen):
                func_name = value[idx].split('<----->')[0]
                parm_name = value[idx].split('<----->')[1]
                parm_value = value[idx].split('<----->')[2]
                if func_name != fn_temp or parm_name in pnames:
                    if fn_temp == 'gen_init':
                        spider_name = sname[0].upper() + sname[1:] + 'Spider'
                        pvalues.insert(0, spider_name)
                    code = eval(fn_temp) % tuple(pvalues) if pvalues and fn_temp != 'save_product' else eval(fn_temp)
                    fh.write(code)
                    fh.write(generator_append)
                    pnames, pvalues = [], []
                update_element_record(session, spider_id, idx+1, func_name, parm_name, parm_value)
                pnames.append(parm_name)
                pvalues.append(parm_value)
                fn_temp = func_name
            code = eval(func_name) % tuple(pvalues) if pvalues != [''] else eval(func_name)
            fh.write(code)
            fh.write(generator_append)
            
            script_name_fin = sname + '.py'
            script_name_fp = os.path.join(script_save_path, script_name_fin)
            generator_loop_code = generator_loop(script_name_fp)
            fh.write(generator_loop_code)
            fh.close()
            
            source_conf_name = sname + '.json'
            source_conf_fp = os.path.join(json_save_path, source_conf_name)
            save_source_json(source_id[0], source_conf_fp)
            
            ex_cmd = execute_generator_cmd % (generator_name)
            generate_log = commands.getoutput(ex_cmd)
            if generate_log:
                self.write_json("Generate_log is :    " + generate_log[-2000:], 200)
            else:
                self.write_json("Spider has been created!", 200)
        except Exception, e:
            self.write_json("Server internal error! Please contact the administrator. %s" % (traceback.format_exc()), 200)
        finally:
            close_session(engine, session)
            self.finish()

def read_csv(filename, content):
    with open(filename,  'r') as filehandle:
        reader = csv.DictReader(filehandle, delimiter=',')
        for row in reader:
            content.append(row)

def search_csv_folder(csv_type, source_id):
    content = []
    for spath in scripts_path:
        for root,dirs,files in os.walk(spath,True):
            for file in files:
                if csv_type in file and source_id in file:
                    read_csv(os.path.join(spath, file), content)
    return content

def remove_csv_by_sid(source_id):
    for spath in scripts_path: 
        del_cmd = 'rm -rf %s*%s*' % (spath, source_id)
        os.system(del_cmd)	
    
class ExcuteScriptHandler(JSONHandler):
    def get(self):
        ip = self.request.remote_ip
        script_name = self.get_argument('script_name', '')
        source_id = self.get_argument('source_id', '')
        if script_name and source_id:
            script_name = script_name.lower().replace('-', '_').replace('.py', '')
            con_identification = hashlib.md5(ip + '_' + source_id).hexdigest()
            if source_id in source_id_testing:
                self.write_json("This source is already in testing! Please wait for a while and then try again. ", 200)
            else:
                remove_csv_by_sid(source_id)
                source_content_cache[con_identification] = {}
                source_id_testing[source_id] = ''
                source_id_testing[con_identification] = ''
                source_signal[con_identification] = False
                scheduler = BackgroundScheduler(daemonic = True)
                scheduler.add_job(self.kill_crawl_process, 'interval', minutes=script_execution_duration, id='kill_crawl_process', args=[script_name, scheduler, 'kill_crawl_process'])
                scheduler.add_job(self.remove_source_content_cache, 'interval', minutes=source_content_cache_duration, id='remove_source_content_cache', args=[con_identification, scheduler, 'remove_source_content_cache'])
                scheduler.start()
                ex_cmd = 'scrapy crawl ' + script_name
                debug_log = commands.getoutput(ex_cmd)
                source_signal[con_identification] = True
                self.write_json("Debug_log is :    " + debug_log, 200)
        self.finish()

    def remove_source_content_cache(self, con_identification, scheduler, job_name):
        if con_identification in source_content_cache:
            source_content_cache.pop(con_identification)
        scheduler.remove_job(job_name)
        
    def kill_crawl_process(self, script_name, scheduler, job_name):
        process_list = list(psutil.process_iter())
        for process in process_list:
            cmd_line = process.cmdline()
            if process.name() == 'scrapy' and 'crawl' in cmd_line and script_name in cmd_line:
                kill_cmd = 'kill -9 ' + str(process.pid)
                os.system(kill_cmd)
        scheduler.remove_job(job_name)


class TestSpiderPidHandler(JSONHandler):
    def post(self):
        ip = self.request.remote_ip
        source_id = self.get_argument('source_id', '')
        page = self.get_argument('page', '')
        rows = self.get_argument('rows', '')
        idx = (int(page) - 1) * int(rows)
        if source_id:
            con_identification = hashlib.md5(ip + '_' + source_id).hexdigest()
            if con_identification in source_id_testing and source_signal[con_identification] == True:
                content = search_csv_folder('product_id', source_id)
                source_content_cache[con_identification]['pid'] = content
                self.write_json_page(content, idx, page, rows)
            if int(page) > 1 and source_signal[con_identification] == True:
                content = source_content_cache[con_identification]['pid']
                self.write_json_page(content, idx, page, rows)
        self.finish()
        
class TestSpiderProHandler(JSONHandler):
    def post(self):
        ip = self.request.remote_ip
        source_id = self.get_argument('source_id', '')
        page = self.get_argument('page', '')
        rows = self.get_argument('rows', '')
        idx = (int(page) - 1) * int(rows)
        if source_id:
            con_identification = hashlib.md5(ip + '_' + source_id).hexdigest()
            if con_identification in source_id_testing and source_signal[con_identification] == True:
                content = search_csv_folder('products', source_id)
                source_content_cache[con_identification]['pro'] = content
                self.write_json_page(content, idx, page, rows)
            if int(page) > 1 and source_signal[con_identification] == True:
                content = source_content_cache[con_identification]['pro']
                self.write_json_page(content, idx, page, rows)
        self.finish()
        
class TestSpiderRevHandler(JSONHandler):
    def post(self):
        ip = self.request.remote_ip
        source_id = self.get_argument('source_id', '')
        page = self.get_argument('page', '')
        rows = self.get_argument('rows', '')
        idx = (int(page) - 1) * int(rows)
        if source_id:
            con_identification = hashlib.md5(ip + '_' + source_id).hexdigest()
            if con_identification in source_id_testing and source_signal[con_identification] == True:
                content = search_csv_folder('reviews', source_id)
                source_content_cache[con_identification]['rev'] = content
                self.write_json_page(content, idx, page, rows)
            if int(page) > 1 and source_signal[con_identification] == True:
                content = source_content_cache[con_identification]['rev']
                self.write_json_page(content, idx, page, rows)
        self.finish()
            
class ExcuteOverHandler(JSONHandler):
    def get(self):
        ip = self.request.remote_ip
        source_id = self.get_argument('source_id', '')
        if source_id:
            con_identification = hashlib.md5(ip + '_' + source_id).hexdigest()
            if con_identification in source_id_testing and source_signal[con_identification] == True:
                if source_id in source_id_testing:
                    source_id_testing.pop(source_id)
                if con_identification in source_id_testing:
                    source_id_testing.pop(con_identification)
        self.finish()
        
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class Application(tornado.web.Application):
    def __init__(self):  
        settings = {
            "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url": "/login",
            "xsrf_cookies": False,
            'debug' :True,
        }
        
        handlers = [
            (r"/gen_spider", GenSpiderHandler), #http://remoteserver:port/gen_spider
            (r"/excute_script", ExcuteScriptHandler),
            (r"/save_script", SaveScriptHandler),
            (r"/load_script", LoadScriptHandler),
            (r"/load_pid", TestSpiderPidHandler),
            (r"/load_pro", TestSpiderProHandler),
            (r"/load_rev", TestSpiderRevHandler),
            (r"/", IndexHandler),
            (r"/excute_over", ExcuteOverHandler),
        ]  

        tornado.web.Application.__init__(self, handlers, 
                                         template_path = os.path.join(os.path.dirname(__file__), "templates"),
                                         static_path = os.path.join(os.path.dirname(__file__), "static"),
                                         **settings) 

    
def main():
    PORT = 16688
    application = Application()  
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    ioloop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(ioloop)
    ioloop.start()


if __name__ == "__main__":
    main()
