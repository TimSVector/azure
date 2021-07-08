#parallel_build_execute.py

from __future__ import unicode_literals
import sys, os, subprocess, argparse, glob, shutil
from pprint import pprint
import pdb, time
from datetime import timedelta
from io import open

from vector.apps.DataAPI.vcproject_api import VCProjectApi 
from threading import Thread, Lock
try:
        from Queue import Queue, Empty
except ImportError:
        from queue import Queue, Empty  # python 3.x
 
VCD = os.environ['VECTORCAST_DIR']

class ParallelExecute(object):
    def __init__(self):
        self.manageProject = None
        parser = argparse.ArgumentParser()        
        # running from manage
        
        parser.add_argument('--project', '-p',     help='Manager Project Name')
        parser.add_argument('--incremental', help='Using build-execute incremental (CBT)', action="store_true")
        parser.add_argument('--dryrun',      help='Dry Run without build/execute', action="store_true")
        parser.add_argument('--verbose',     help='Dry Run without build/execute', action="store_true")
        parser.add_argument('--jobs', '-j',     help='Number of concurrent jobs (default = 1)', default="1")
        args = parser.parse_args()
        
        try:
            self.manageProject = os.environ['VCV_ENVIRONMENT_FILE']
        except:
            self.manageProject = args.project

        self.jobs = args.jobs
        self.dryrun = args.dryrun
            
        if self.manageProject is None:
            print ("\n** Use either --project [Manage Project Name] or enviroment variable VCV_ENVIRONMENT_FILE to specify the manage project name")
            sys.exit()
        
        if not os.path.isfile(self.manageProject) and not os.path.isfile(self.manageProject + ".vcm"):
            raise IOError(self.manageProject + ' does not exist')
            return
            
        if args.incremental:
            self.incremental = "--incremental"
        else:
            self.incremental = ""
            
        if args.verbose:
            self.verbose = True
        else:
            self.verbose = False
            
        self.currently_executing_jobs = []
        self.jobs_run_time = {}
        self.script_start_time = time.time()

        self.running_jobs = 0
        self.lock = Lock()
        self.system_test_lock = Lock()
        self.mpName = self.manageProject.replace(".vcm","")
        
    def th_Print (self, str):
        self.lock.acquire()
        print (str)
        self.lock.release()
                
    def th_lock_acquire(self):
        self.lock.acquire()
        
    def th_lock_release(self):
        self.lock.release()
        
    def run_env(self, env_in, queue, exec_queue, is_system_test):
        
        if is_system_test:
            self.system_test_lock.acquire()
            
        self.th_lock_acquire()
        self.running_jobs += 1
        self.th_lock_release()
        
        compiler, testsuite, env = env_in.split()
        level = compiler + "/" + testsuite
        full_name = "/".join([compiler, testsuite, env])
        exec_cmd = VCD + "/manage --project " + self.manageProject + \
            " --build-execute " + self.incremental + " --level " + level + \
            " --environment " + env + \
            " --output " + "_".join([compiler, testsuite, env])+ "_rebuild.html"
            

        build_log = open(".".join(["build",compiler, testsuite, env,"log"]),"w")
        
        start_time = time.time()
        if not self.dryrun:
            process = subprocess.Popen(exec_cmd, shell=True, stdout=build_log, stderr=build_log)    
            process.wait()
        else:
            if self.verbose:
                self.th_Print ("RUN>> " + exec_cmd)
            else:
                self.th_Print ("RUN>> " + full_name )
            
        end_time = time.time()
        uptime = end_time - start_time
        human_uptime = str(timedelta(seconds=int(uptime)))
        self.jobs_run_time[full_name] = human_uptime
        

        build_log.close()
        
        #print ("Harness Loading/Execution", full_name, "Complete")
        exec_queue.get()
        queue.task_done()
        
        self.th_lock_acquire()
        self.currently_executing_jobs.remove(full_name)
        self.th_lock_release()
        
        self.th_lock_acquire()
        self.running_jobs -= 1
        self.th_lock_release()
        
        if is_system_test:
            self.system_test_lock.release()

    def run_compiler(self, compiler, max, queue, compiler_queue):
        ##pdb.set_trace()        
        compiler_queue.get()
        
        parallel_exec_queue = Queue(maxsize=max)
        
        while not queue.empty():
            q_entry =  queue.get()
            env = q_entry[0]
            isSystemTest = q_entry[1]
            self.th_lock_acquire()
            self.currently_executing_jobs.append("/".join(env.split()))
            self.th_lock_release()
            
            parallel_exec_queue.put(env)
            t = Thread(target=self.run_env, args=[env, queue, parallel_exec_queue, isSystemTest])
            t.daemon = True # thread dies with the program
            t.start()

        queue.join()
        
        compiler_queue.task_done()
    
    def monitor_jobs(self):
        
        while self.running_jobs != 0:
            print ("\n\nWaiting on jobs (", self.running_jobs , len(self.currently_executing_jobs), "}")
            print ("===============\n  ")
            si = self.currently_executing_jobs
            si.sort()
            print ("  " + "\n  ".join(si))
            
            for compiler in self.waiting_execution_queue:
                qsz = self.waiting_execution_queue[compiler].qsize()
                if qsz > 0:
                    print ("  >> ", compiler, "has", qsz,  "environment(s) in queue")
            
            time.sleep(3)

        print ("waiting for jobs to finalize"    )
        self.compiler_exec_queue.join()
        script_end_time = time.time()
        script_uptime = script_end_time - self.script_start_time
        script_human_uptime = str(timedelta(seconds=int(script_uptime)))

        subprocess.call(VCD + "/manage --project " + self.manageProject + " --full-status")

        print ("\n\nSummary of Parallel Execution")
        print (    "=============================")
        print ("  Total time :", script_human_uptime)
        for job in self.jobs_run_time:
            print ("  ", self.jobs_run_time[job], job)

    def parse_html_files(self):

        from bs4 import BeautifulSoup
        report_file_list = []
        full_file_list = os.listdir(".")
        for file in glob.glob("*_rebuild.html"):
            report_file_list.append(file)

        if len(report_file_list) == 0:
            print("  No incrementatal rebuild reports found in the workspace...skipping")
            return
            
        try:
            main_soup = BeautifulSoup(open(report_file_list[0]),features="lxml")
        except:
            main_soup = BeautifulSoup(open(report_file_list[0]))
            
        preserved_count = 0
        executed_count = 0
        total_count = 0
        if main_soup.find(id="report-title"):
            main_manage_api_report = True
            # New Manage reports have div with id=report-title
            # Want second table (skip config data section)
            main_row_list = main_soup.find_all('table')[1].tr.find_next_siblings()
            main_count_list = main_row_list[-1].th.find_next_siblings()
        else:
            main_manage_api_report = False
            main_row_list = main_soup.table.table.tr.find_next_siblings()
            main_count_list = main_row_list[-1].td.find_next_siblings()

        preserved_count = preserved_count + int(main_count_list[1].get_text())
        executed_count = executed_count + int(main_count_list[2].get_text())
        total_count = total_count + int(main_count_list[3].get_text())
        if main_manage_api_report:
            build_success, build_total = [int(s.strip()) for s in main_count_list[0].get_text().strip().split('(')[0][:-1].split('/')]
        else:
            build_success, build_total = [int(s.strip()) for s in main_count_list[0].get_text().strip().split('(')[-1][:-1].split('/')]
        
        insert_idx = 2
        for file in report_file_list[1:]:
            try:
                soup = BeautifulSoup(open(file),features="lxml")
            except:
                soup = BeautifulSoup(open(file))
            if soup.find(id="report-title"):
                manage_api_report = True
                # New Manage reports have div with id=report-title
                # Want second table (skip config data section)
                row_list = soup.find_all('table')[1].tr.find_next_siblings()
                count_list = row_list[-1].th.find_next_siblings()
            else:
                manage_api_report = False
                row_list = soup.table.table.tr.find_next_siblings()
                count_list = row_list[-1].td.find_next_siblings()
            for item in row_list[:-1]:
                if manage_api_report:
                    main_soup.find_all('table')[1].insert(insert_idx,item)
                else:
                    main_soup.table.table.insert(insert_idx,item)
                insert_idx = insert_idx + 1
            preserved_count = preserved_count + int(count_list[1].get_text())
            executed_count = executed_count + int(count_list[2].get_text())
            total_count = total_count + int(count_list[3].get_text())
            if manage_api_report:
                build_totals = [int(s.strip()) for s in count_list[0].get_text().strip().split('(')[0][:-1].split('/')]
            else:
                build_totals = [int(s.strip()) for s in count_list[0].get_text().strip().split('(')[-1][:-1].split('/')]
            build_success = build_success + build_totals[0]
            build_total = build_total + build_totals[1]

        try:
            percentage = build_success * 100 // build_total
        except:
            percentage = 0
        if main_manage_api_report:
            main_row_list = main_soup.find_all('table')[1].tr.find_next_siblings()
            main_count_list = main_row_list[-1].th.find_next_siblings()
            main_count_list[0].string.replace_with(str(build_success) + " / " + str(build_total) + " (" + str(percentage) + "%)" )
        else:
            main_row_list = main_soup.table.table.tr.find_next_siblings()
            main_count_list = main_row_list[-1].td.find_next_siblings()
            main_count_list[0].string.replace_with(str(percentage) + "% (" + str(build_success) + " / " + str(build_total) + ")")

        main_count_list[1].string.replace_with(str(preserved_count))
        main_count_list[2].string.replace_with(str(executed_count))
        main_count_list[3].string.replace_with(str(total_count))

        # moving rebuild reports down in to a sub directory
        f = open(self.mpName + "_incremental_rebuild_report.html","w", encoding="utf-8")
        f.write(main_soup.prettify(formatter="html"))
        f.close()
        
        # moving rebuild reports down in to a sub directory
        if not os.path.exists("rebuild_reports"):
            os.mkdir("rebuild_reports")
        for file in report_file_list:
            if os.path.exists(file):
              shutil.move(file, "rebuild_reports/"+file)  
              
    def cleanup(self):
                
        print ("\n\n")
        
        build_log_data = ""
        for file in glob.glob("build*.log"):
            build_log_data += "\n".join(open(file,"r").readlines())
            os.remove(file)
            
        open(self.mpName + "_build.log","w", encoding="utf-8").write(build_log_data)
        
        if self.incremental:
            self.parse_html_files()
        
    def doit(self):
        api = VCProjectApi(self.manageProject)
              
        self.parallel_exec_info = {}
        self.waiting_execution_queue = {}

        for env in api.Environment.all():

            count = int(self.jobs)
            def_list = env.options['enums']['C_DEFINE_LIST'][0]
            if "VCAST_PARALLEL_PROCESS_COUNT" in def_list:
                li = def_list.split()
                for item in li:
                    if "VCAST_PARALLEL_PROCESS_COUNT" in item:
                        count = int(item.split("=")[-1])
                
            self.parallel_exec_info[env.compiler.name] = (count, [])

        for env in api.Environment.all():
            if env.system_tests: 
                isSystemTest = True
            else:
                isSystemTest = False
                
            compiler = env.compiler.name
            if compiler in self.parallel_exec_info:
                env_list = self.parallel_exec_info[compiler][1]
                full_name = env.compiler.name + " " + env.testsuite.name + " " + env.name
                env_list.append([full_name, isSystemTest])
                self.waiting_execution_queue[compiler] = Queue()
                
                #waiting_execution_queue[compiler].append(full_name)
                

        for entry in self.parallel_exec_info:
            count = self.parallel_exec_info[entry][0]
            for item in self.parallel_exec_info[entry][1]:
                compiler, testsuite, env = item[0].split()
                self.waiting_execution_queue[compiler].put(item)
                

        ## start threads that start threads
        self.compiler_exec_queue = Queue()

        for compiler in self.waiting_execution_queue:
            max = self.parallel_exec_info[compiler][0]
            
            t = Thread(target=self.run_compiler, args=[compiler, max, self.waiting_execution_queue[compiler], self.compiler_exec_queue],)
            self.compiler_exec_queue.put(t)
            t.daemon = True # thread dies with the program
            t.start()

        ## Quiet down period
        time.sleep(1)
        
        self.monitor_jobs()
        
        self.cleanup()
        
if __name__ == '__main__':
    ParallelExecute().doit()

