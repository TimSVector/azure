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

import os, subprocess,argparse, glob, sys

from managewait import ManageWait
from parse_console_for_cbt import ParseConsoleForCBT
import generate_results 
import cobertura


class AzureExecute(object):
    def __init__(self, ManageProject, useCILicense, useCBT, level, environment, verbose, print_exc, timing, buildlog):

        # setup default values
        self.print_exc = print_exc
        self.timing = timing

        self.verbose = verbose
        self.FullMP = ManageProject
        self.mpName = os.path.basename(ManageProject)[:-4]

        if useCILicense:
            self.useCI = " --ci "
        else:
            self.useCI = ""

        if useCBT:
            self.useCBT = " --incremental "
        else:
            self.useCBT = ""

        self.build_log = None
                    
        self.useLevelEnv = False
        self.environment = None
        self.level = None
        self.compiler = ""
        self.testsuite = ""
        self.reportsName = ""
        self.env_option = ""
        self.level_option = ""
        self.build_log_name = buildlog

        # if a manage level was specified...
        if level:        
            self.useLevelEnv = True
            self.level = level
            
            # try level being Compiler/TestSuite
            try:
                self.compiler, self.testsuite = level.split("/")
                self.reportsName = "_" + self.compiler + "_" + self.testsuite
            except:
                # just use the compiler name
                self.compiler = level
                self.reportsName = "_" + self.compiler
                
            self.level_option = "--level " + level + " "

        # if an environment was specified
        if environment:
            # afix the proper settings for commands later and report names
            self.useLevelEnv = True
            self.environment = environment
            self.env_option = "--environment " + environment + " "
            self.reportsName += "_" + self.environment
                  
        if self.useLevelEnv:
            self.build_log_name = "build" + self.reportsName + ".log"    

        self.manageWait = ManageWait(self.verbose, "", 30, 1, self.FullMP, self.useCI)

    def runMetrics(self):
        # read in build log for CBT analysis               
        if os.path.exists(self.build_log_name):
            print ("Using build log: " + self.build_log_name)
            self.build_log = open(self.build_log_name,"r").read()
            
        else:
            print ("Build log not found. Trying to generate complete log from individual build logs")
            self.build_log = ""
            for file in glob.glob("build*.log"):
                if self.verbose: print(file)
                self.build_log += open(file,"r").read() + "\n" 
            
        cbt = ParseConsoleForCBT(args.verbose)
        cbtDict = None
        
        # don't show skipped tests as Azure shows them as "Other" instead of skipped
#        if self.build_log:
#            cbtDict = cbt.parse(self.build_log)
#        else:
#            print("Could not find any build logs...skipping CBT Analysis")
            
        generate_results.verbose = self.verbose
        generate_results.print_exc = self.print_exc
        generate_results.timing = self.timing
        generate_results.buildReports(self.FullMP,self.level,self.environment, True, self.timing, cbtDict)

        for file in glob.glob("xml_data/coverage_results_*.*"):
            try:
                os.remove(file);
            except:
                print("Error removing file after failed to remove directory: " +  file)
        cobertura.azure = True
        cobertura.generateCoverageResults(self.FullMP)

    def runReports(self):
        self.manageWait.exec_manage_command ("--create-report=aggregate     --output=" + self.mpName + "_aggregate_report.html")
        self.manageWait.exec_manage_command ("--create-report=metrics       --output=" + self.mpName + "_metrics_report.html")
        self.manageWait.exec_manage_command ("--create-report=environment   --output=" + self.mpName + "_environment_report.html")

    def runExec(self):

        self.manageWait.exec_manage_command ("--status")
        self.manageWait.exec_manage_command ("--force --release-locks")
        self.manageWait.exec_manage_command ("--config VCAST_CUSTOM_REPORT_FORMAT=HTML")
        
        if self.useLevelEnv:
            output = "--output " + self.mpName + self.reportsName + "_rebuild.html"
        else:
            output = ""
            
        self.build_log = self.manageWait.exec_manage_command ("--build-execute " + self.useCBT + self.level_option + self.env_option + output )
        open(self.build_log_name,"w").write(self.build_log)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('ManageProject', help='Manager Project Name')
    parser.add_argument('--ci', help='Use CI Licenses', action="store_true", default = False)
    parser.add_argument('--incremental', help='Use CBT', action="store_true", default = False)
    parser.add_argument('--execute', help='Exeuction the VectorCAST Project', action="store_true", default = False)
    parser.add_argument('--metrics', help='Run the metrics for VectorCAST Project', action="store_true", default = False)
    parser.add_argument('--reports', help='Run the reports for VectorCAST Project', action="store_true", default = False)
    parser.add_argument('--print_exc', help='Prints exceptions', action="store_true", default = False)
    parser.add_argument('--buildlog', help='VectorCAST Build Log', default = "complete_build.log")
    parser.add_argument('--timing', help='Prints timing information for metrics generation', action="store_true", default = False)
    parser.add_argument('-v', '--verbose',   help='Enable verbose output', action="store_true", default = False)
    parser.add_argument('-l', '--level',   help='Environment Name if only doing single environment.  Should be in the form of level/env')
    parser.add_argument('-e', '--environment',   help='Environment Name if only doing single environment.  Should be in the form of level/env')

    args = parser.parse_args()


    if not os.path.isfile(args.ManageProject):
        print ("Manage project (.vcm file) provided does not exist: " + args.ManageProject)
        print ("exiting...")
        sys.exit(-1)

    glExec = AzureExecute(args.ManageProject, args.ci, args.incremental, args.level, args.environment, args.verbose, args.print_exc, args.timing, args.buildlog)

    if args.execute:
        glExec.runExec()
        
    if args.metrics:
        glExec.runMetrics()

    if args.reports:
        glExec.runReports()
