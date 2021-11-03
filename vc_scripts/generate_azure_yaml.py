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

#generate_gitlab_yaml.py

import argparse, os
from vector.apps.DataAPI.vcproject_api import VCProjectApi

if os.name == 'nt':
    script_cmds = """
    - Start-Process -NoNewWindow -wait ./setenv.bat
    - Start-Process -NoNewWindow -wait $env:VECTORCAST_DIR\\vpython.exe  -ArgumentList ".\\vc_scripts\\gitlab_exec.py "$VC_Manage_Project" $VC_UseCILicense $VC_useCBT --level %s/%s --environment %s --execute"
    """
    
    reporting_cmds = """
    - Start-Process -NoNewWindow -wait ./setenv.bat
    - Start-Process -NoNewWindow -wait $env:VECTORCAST_DIR\\vpython.exe  -ArgumentList ".\\vc_scripts\\gitlab_exec.py "$VC_Manage_Project" $VC_UseCILicense $VC_useCBT --reports --metrics"
    """
else:
    script_cmds = """
    - source ./setenv.sh
    - $VECTORCAST_DIR/vpython ./vc_scripts/gitlab_exec.py "$VC_Manage_Project" $VC_UseCILicense $VC_useCBT --level %s/%s --environment %s --execute"""
    
    reporting_cmds = """
    - source ./setenv.sh
    - $VECTORCAST_DIR/vpython ./vc_scripts/gitlab_exec.py "$VC_Manage_Project" $VC_UseCILicense $VC_useCBT --reports --metrics"""
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('ManageProject', help='Manager Project Name')
    parser.add_argument('--ci', help='Use CI Licenses', action="store_true", default = False)
    parser.add_argument('--incremental', help='Use CBT', action="store_true", default = False)

    args = parser.parse_args()

    
    if args.ci:
        useCI = "--ci"
    else:
        useCI = ""
        
    if args.incremental:
        useCBT = "--incremental"
    else:
        useCBT = ""
        
    yaml_start = """stages: [build-execute, reporting, check-logs]
    
variables:
    GIT_CLEAN_FLAGS: none
    VC_Manage_Project: "%s"
    VC_UseCILicense: "%s"
    VC_useCBT: "%s"

""" % (args.ManageProject.replace("\\","/"), useCI, useCBT)

    api = VCProjectApi(args.ManageProject)
    
    # individual build stages
    build_stage_template = """%s:
  stage: build-execute
  script: """ + script_cmds + """
  tags:
    - %s

"""    
    build_stage = ""
    for env in api.Environment.all():
        if env.compiler.is_enabled:
            jobName = "build-execute-" + env.compiler.name.lower() + "-" + env.testsuite.name.lower() + "-" + env.name.lower()
            build_stage += build_stage_template % (jobName, env.compiler.name, env.testsuite.name, env.name, env.compiler.name)

    yaml_end = """reporting:
  stage: reporting
  script: """ + reporting_cmds + """
  tags:
    - vectorcast
    
  artifacts:
    untracked: false
    expire_in: 30 days    
    paths:
      - xml_data/test_results*.xml
      - xml_data/coverage_results*.xml
      - html_reports/*.html
      - ./*.html
    reports:
      junit: xml_data/test_results*.xml
      cobertura: xml_data/coverage_results*.xml

check-logs:
  stage: check-logs
  script: "echo check-logs"
  tags:
    - vectorcast

"""

f = open("vectorcast_execute.yml","w")
f.write(yaml_start)
f.write(build_stage)
f.write(yaml_end)
f.close()

