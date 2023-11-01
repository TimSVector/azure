#
# The MIT License
#
# Copyright 2020 Vector Informatik, GmbH.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os, subprocess,argparse, glob, sys, shutil

from managewait import ManageWait
import generate_results 
import cobertura

try:
    import vector.apps.parallel.parallel_build_execute as parallel_build_execute
except:
    import prevcast_parallel_build_execute as parallel_build_execute

class VectorCASTExecute(object):

    def __init__(self, args):

        # setup default values
        self.azure = args.azure
        self.gitlab = args.gitlab
        self.print_exc = args.print_exc
        self.print_exc = args.print_exc
        self.timing = args.timing
        self.jobs = args.jobs
        self.sonarqube = args.sonarqube
        self.junit = args.junit
        self.cobertura = args.cobertura
        self.metrics = args.metrics
        self.aggregate = args.aggregate
        
        if args.build and not args.build_execute:
            self.build_execute = "build"
            self.vcast_action = "--vcast_action " + self.build_execute
        elif args.build_execute:
            self.build_execute = "build-execute"
            self.vcast_action = "--vcast_action " + self.build_execute
        else:
            self.build_execute = ""
            self.vcast_action = ""
        
        self.verbose = args.verbose
        self.FullMP = args.ManageProject
        self.mpName = os.path.basename(args.ManageProject)[:-4]

        if args.ci:
            self.useCI = " --use_ci "
            self.ci = " --ci "
        else:
            self.useCI = ""
            self.ci = ""
            
        if args.incremental:
            self.useCBT = " --incremental "
        else:
            self.useCBT = ""
                  
        self.useLevelEnv = False
        self.environment = None
        self.level = None
        self.compiler = None
        self.testsuite = None
        self.reportsName = ""
        self.env_option = ""
        self.level_option = ""

        # if a manage level was specified...
        if args.level:        
            self.useLevelEnv = True
            self.level = args.level
            
            # try level being Compiler/TestSuite
            try:
                self.compiler, self.testsuite = args.level.split("/")
                self.reportsName = "_" + self.compiler + "_" + self.testsuite
            except:
                # just use the compiler name
                self.compiler = args.level
                self.reportsName = "_" + self.compiler
                
            self.level_option = "--level " + args.level + " "

        # if an environment was specified
        if args.environment:
            # afix the proper settings for commands later and report names
            self.useLevelEnv = True
            self.environment = args.environment
            self.env_option = "--environment " + args.environment + " "
            self.reportsName += "_" + self.environment
                  
        if self.useLevelEnv:
            self.build_log_name = "build" + self.reportsName + ".log"    
        else:
            self.build_log_name = "build" + self.mpName + ".log"    

        self.manageWait = ManageWait(self.verbose, "", 30, 1, self.FullMP, self.ci)
            
        self.cleanup("junit", "test_results_")
        self.cleanup("cobertura", "coverage_results_")
        self.cleanup("sonarqube", "test_results_")
        self.cleanup(".", self.mpName + "_aggregate_report.html")
        self.cleanup(".", self.mpName + "_metrics_report.html")
        
    def cleanup(self, dirName, fname):
        for file in glob.glob("xml_data/" + dirName+ "/" + fname + "*.*"):
            try:
                os.remove(file);
            except:
                print("Error removing file after failed to remove directory: " +  file)
                
        try:
            shutil.rmtree("xml_data/" + dirName)
        except:
            pass

    
    def runJunitMetrics(self):
        print("Creating JUnit Metrics")

        generate_results.verbose = self.verbose
        generate_results.print_exc = self.print_exc
        generate_results.timing = self.timing
        generate_results.buildReports(self.FullMP,self.level,self.environment, True, self.timing)
            

    def runCoberturaMetrics(self):
        print("Creating Cobertura Metrics")
        cobertura.verbose = self.verbose
        cobertura.generateCoverageResults(self.FullMP, self.azure)

    def runSonarQubeMetrics(self):
        print("Creating SonarQube Metrics")
        import generate_sonarqube_testresults 
        generate_sonarqube_testresults.run(self.FullMP)

    def runReports(self):
        if self.aggregate:
            self.manageWait.exec_manage_command ("--create-report=aggregate     --output=" + self.mpName + "_aggregate_report.html")
        if self.metrics:
            self.manageWait.exec_manage_command ("--create-report=metrics       --output=" + self.mpName + "_metrics_report.html")

    def runExec(self):

        self.manageWait.exec_manage_command ("--status")
        self.manageWait.exec_manage_command ("--force --release-locks")
        self.manageWait.exec_manage_command ("--config VCAST_CUSTOM_REPORT_FORMAT=HTML")
        
        if self.useLevelEnv:
            output = "--output " + self.mpName + self.reportsName + "_rebuild.html"
        else:
            output = ""
            
        if self.jobs != "1":

            # should work for pre-vcast parallel_build_execute or vcast parallel_build_execute
            pstr = "--project " + self.FullMP
            jstr = "--jobs="+str(self.jobs)
            cstr = "" if (self.compiler == None) else "--compiler="+self.compiler
            tstr = "" if (self.testsuite == None) else "--testsuite="+self.testsuite
            cbtStr = self.useCBT
            ciStr = self.useCI
            vbStr = "--verbose" if (self.verbose) else ""
            
            # filter out the blank ones
            callList = []
            for s in [pstr, jstr, cstr, tstr, cbtStr, ciStr, vbStr, self.vcast_action]:
                if s != "":
                    s = s.strip()
                    callList.append(s)

            callStr = " ".join(callList)
            parallel_build_execute.parallel_build_execute(callStr)

        else:      
            cmd = "--" + self.build_execute + " " + self.useCBT + self.level_option + self.env_option + output 
            build_log = self.manageWait.exec_manage_command (cmd)
            open(self.build_log_name,"w").write(build_log)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('ManageProject', help='Manager Project Name')
    
    actionGroup = parser.add_argument_group('Script Actions', 'Options for the main tasks')
    actionGroup.add_argument('--build-execute', help='Builds and exeuctes the VectorCAST Project', action="store_true", default = False)
    parser_specify = actionGroup.add_mutually_exclusive_group()
    parser_specify.add_argument('--build',       help='Only builds the VectorCAST Project', action="store_true", default = False)
    parser_specify.add_argument('--incremental', help='Use Change Based Testing (Cannot be used with --build)', action="store_true", default = False)

    metricsGroup = parser.add_argument_group('Metrics Options', 'Options generating metrics')
    metricsGroup.add_argument('--cobertura', help='Builds and exeuctes the VectorCAST Project', action="store_true", default = False)
    metricsGroup.add_argument('--junit', help='Builds and exeuctes the VectorCAST Project', action="store_true", default = False)
    metricsGroup.add_argument('--sonarqube', help='Generate test results in SonarQube Generic test execution report format (CppUnit)', action="store_true", default = False)

    reportGroup = parser.add_argument_group('Report Selection', 'VectorCAST Manage reports that can be generated')
    reportGroup.add_argument('--aggregate', help='Generate aggregate coverage report VectorCAST Project', action="store_true", default = False)
    reportGroup.add_argument('--metrics', help='Genenereate metrics reports for VectorCAST Project', action="store_true", default = False)

    beGroup = parser.add_argument_group('Build/Execution Options', 'Options that effect build/execute operation')
    
    beGroup.add_argument('--jobs', help='Number of concurrent jobs (default = 1)', default="1")
    beGroup.add_argument('--ci', help='Use Continuous Integration Licenses', action="store_true", default = False)
    beGroup.add_argument('-l', '--level',   help='Environment Name if only doing single environment.  Should be in the form of compiler/testsuite', default=None)
    beGroup.add_argument('-e', '--environment',   help='Environment Name if only doing single environment.', default=None)

    parser_specify = beGroup.add_mutually_exclusive_group()
    parser_specify.add_argument('--gitlab', help='Build using GitLab CI (default)', action="store_true", default = True)
    parser_specify.add_argument('--azure',  help='Build using Azure DevOps', action="store_true", default = False)

    actionGroup = parser.add_argument_group('Script Debug ', 'Options used for debugging the script')
    actionGroup.add_argument('--print_exc', help='Prints exceptions', action="store_true", default = False)
    actionGroup.add_argument('--timing', help='Prints timing information for metrics generation', action="store_true", default = False)
    actionGroup.add_argument('-v', '--verbose',   help='Enable verbose output', action="store_true", default = False)
    

    args = parser.parse_args()
    
    if args.ci:
        os.environ['VCAST_USE_CI_LICENSES'] = "1"
        
    os.environ['VCAST_MANAGE_PROJECT_DIRECTORY'] = os.path.abspath(args.ManageProject).rsplit(".",1)[0]

    if not os.path.isfile(args.ManageProject):
        print ("Manage project (.vcm file) provided does not exist: " + args.ManageProject)
        print ("exiting...")
        sys.exit(-1)

    vcExec = VectorCASTExecute(args)

    if args.build_execute or args.build:
        vcExec.runExec()
        
    if args.cobertura:
        vcExec.runCoberturaMetrics()

    if args.junit:
        vcExec.runJunitMetrics()

    if args.sonarqube:
        vcExec.runSonarQubeMetrics()

    if args.aggregate or args.metrics:
        vcExec.runReports()
		
