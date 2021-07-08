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

from lxml import etree
from vector.apps.DataAPI.vcproject_api import VCProjectApi 
from vector.apps.DataAPI.vcproject_models import VCProject
from vector.apps.DataAPI.cover_api import CoverApi
from vector.apps.DataAPI.unit_test_api import UnitTestApi
import sys, os
from collections import defaultdict


fileList = []
global gitlab
gitlab = False

global azure
azure = False

def write_xml(x, name, verbose = False):
    global azure
    
    if verbose:
        print(etree.tostring(x,pretty_print=True))

    if azure:
        xml_str = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    else:
        xml_str = ""
    
    xml_str += etree.tostring(x,pretty_print=True).decode()

    open(name + ".xml", "w").write(xml_str)
   

def getFileXML(testXml, coverAPI):

    global gitlab
    
    fname = coverAPI.path
    
    cov_br_pct = coverAPI.metrics.covered_branches_pct / 100.0
    st_br_pct = coverAPI.metrics.covered_statements_pct / 100.0
    
    file = None
    
    if gitlab:
        checkName = fname
    else:
        checkName = os.path.basename(fname)
        
    for element in testXml.iter():
        if element.tag == "class" and element.attrib['filename'] == checkName:
            file = element
            lines = file[0]
        
    if file == None:
        file = etree.SubElement(testXml, "class")
        file.attrib['branch-rate'] = str(cov_br_pct)
        file.attrib['complexity'] = str(coverAPI.metrics.complexity)
        file.attrib['filename'] = checkName
        file.attrib['line-rate'] = str(st_br_pct)
        file.attrib['name'] = os.path.basename(fname).replace(".","_")
        lines = etree.SubElement(file, "lines")
        path = os.path.dirname(fname)
        if path not in fileList:
            fileList.append(path)
        
    return lines

#  <coverage branch-rate="0.621853898097" line-rate="0.0848430253895" timestamp="1356956242" version="gcovr 2.5-prerelease (r2774)">
# XX  <sources>
# XX     <source>
# XX       C:\gitlab\project
# XX     </source>
# XX   </sources>
#    <packages>
#      <package branch-rate="0.607142857143" complexity="0.0" line-rate="0.22962962963" name="Common">
#        <classes>
#          <class branch-rate="0.5" complexity="0.0" filename="CommonLibrary\ProfilerTest.cpp" line-rate="0.0869565217391" name="BasicProfilerTest_cpp">
#          <lines>
#            <line branch="false" hits="0" number="30"/>
#            <line branch="false" hits="0" number="32"/>
#            <line branch="true" condition-coverage="50% (2/4)" hits="3" number="161">
#            <conditions>
#              <condition coverage="50%" number="0" type="jump"/>
#            </conditions>
#            </line>
#            <line branch="false" hits="0" number="125"/>
#          </lines>
#          </class>
#        </classes>
#      </package>     
#    </packages>     
#  </coverage>

def getLineCoverageElementXML(lines, lineno):

    covEle = None
    
    for element in lines.iter():
        if element.tag == "line" and element.attrib['number'] == str(lineno):
            covEle = element
        
    if covEle == None:
        covEle = etree.SubElement(lines, "line")
        covEle.attrib['number'] = str(lineno)
        covEle.attrib['hits'] = "0"
        covEle.attrib['branch'] = "false"
        
    return covEle

def getBranchCoverageElementXML(lines, lineno, percent):

    covEle = None
    condition = None
    for element in lines.iter():
        if element.tag == "line" and element.attrib['number'] == str(lineno):
            covEle = element
            if covEle.attrib['branch'] == 'false':
                covEle.attrib['branch'] = 'true'
                covEle.attrib['number'] = str(lineno)
                covEle.attrib['condition-coverage'] = percent
                covEle.attrib['hits'] = "0"
                conditions = etree.SubElement(covEle, "conditions")
                condition = etree.SubElement(conditions, "condition")
            else:
                condition = covEle[0][0]
             
    if covEle == None:
        covEle = etree.SubElement(lines, "line")
        covEle.attrib['number'] = str(lineno)
        covEle.attrib['condition-coverage'] = percent
        covEle.attrib['hits'] = "0"
        covEle.attrib['branch'] = "true"
        conditions = etree.SubElement(covEle, "conditions")
        condition = etree.SubElement(conditions, "condition")
        
    condition.attrib['number'] = "0"
    condition.attrib['type'] = "jump"
    condition.attrib['coverage'] = percent.split()[0]
        
    return covEle

def procesCoverage(coverXML, coverApi):             
    
    
    ## print coverApi
    lines = getFileXML(coverXML, coverApi)
    
    for statement in coverApi.statements:
        covEle = getLineCoverageElementXML(lines,statement.start_line)
        if statement.covered():
            covered = "true"
        else:
            covered = "false"
            
        if statement.start_line == statement.end_line:
            if covEle.attrib['hits'] != "0" or covered == "true":
                covEle.attrib['hits'] = "1"
        else:
            lines.remove(covEle)
            # if its part of a multi-line statement, save the range for use later
            for num in range(statement.start_line,statement.end_line+1):
                covEle = getLineCoverageElementXML(lines,num)
                if covEle.attrib['hits'] != "0" or covered == "true":
                    covEle.attrib['hits'] = "1"
                    
    for branch in coverApi.branches:
        hitFalse = False
        hitTrue  = False
        coveredCount = 0;
        
        num_conditions = branch.num_conditions
        
        if len(branch.get_false_results()) != 0 :
            hitFalse = True
            coveredCount += 1
        if len(branch.get_true_results()) != 0 :
            coveredCount += 1
            hitTrue = True

        percent = 100 * coveredCount / num_conditions
        
        percentStr = str(percent) + "% (" + str(coveredCount) + "/" + str(num_conditions) + ")"         
            
        covEle = getBranchCoverageElementXML(lines,branch.start_line, percentStr)
       
        if hitFalse or hitTrue:
            covEle.attrib['hits'] = "1"
                                 
def runCoverageResultsMP(classes, mpFile):

    vcproj = VCProject(mpFile)
    api = vcproj.cover_api
    
    total_br = 0
    total_st = 0
    cov_br   = 0 
    cov_st   = 0
    vg       = 0

    
    for file in api.File.all():
        total_br += file.metrics.branches
        total_st += file.metrics.statements
        cov_br   += file.metrics.covered_branches
        cov_st   += file.metrics.covered_statements
        vg       += file.metrics.complexity

        procesCoverage(classes, file);
        
    branch_rate = 0.0
    line_rate = 0.0
    
    if total_br > 0:
        branch_rate = float(cov_br) / float(total_br)
        
    if total_st > 0:
        line_rate = float(cov_st) / float(total_st)
        
    return total_st, cov_st, total_br, cov_br, branch_rate, line_rate, vg
            

def generateCoverageResults(inFile):

    global gitlab
    global azure
    
    #coverage results
    coverages=etree.Element("coverage")
    
    if not gitlab:
        sources = etree.SubElement(coverages, "sources")
    packages = etree.SubElement(coverages, "packages")
#   <package branch-rate="0.607142857143" complexity="0.0" line-rate="0.22962962963" name="Common">
    package  = etree.SubElement(packages, "package")
    classes  = etree.SubElement(package, "classes")
    
    branch_rate, line_rate, complexity  = 0.0, 0.0, 0.0
    
    if inFile.endswith(".vce"):
        api=UnitTestApi(inFile)
        #runCoverageResultsUT(classes, api)
    elif inFile.endswith(".vcp"):
        api=CoverAPI(inFile)
        runCoverageCover(classes, api)
    else:        
        total_st, cov_st, total_br, cov_br, branch_rate, line_rate, complexity  = runCoverageResultsMP(classes, inFile)
        
    coverages.attrib['branch-rate'] = str(branch_rate)
    coverages.attrib['line-rate'] = str(line_rate)    
    coverages.attrib['timestamp'] = "0"
    coverages.attrib['version'] = "VectorCAST 2020"
    
    if azure:
        coverages.attrib['lines-covered'] = str(cov_st)
        coverages.attrib['lines-valid'] = str(total_st)
        coverages.attrib['branches-covered'] = str(cov_br)
        coverages.attrib['branches-valid'] = str(total_br)
        
    package.attrib['branch-rate'] = str(branch_rate)
    package.attrib['line-rate'] = str(line_rate)    
    package.attrib['complexity'] = str(complexity)
    name = os.path.splitext(os.path.basename(inFile))[0]
    package.attrib['name'] = name
    print ("coverage: " + str(line_rate*100.0) + "% of statements")
    if not gitlab:
        for path in fileList:
            source = etree.SubElement(sources, "source")
            source.text = path
        
    write_xml(coverages, "xml_data/coverage_results_" + name)
             
if __name__ == '__main__':
    
    inFile = sys.argv[1]
    try:
        if "--gitlab" == sys.argv[2]:
            gitlab = True
            print ("using gitlab mode")
        else:
            gitlab = False
    except Exception as e:
        gitlab = False        

    try:
        if "--azure" == sys.argv[2]:
            azure = True
            print ("using azure mode")
        else:
            azure = False
    except Exception as e:
        azure = False        
        
    generateCoverageResults(inFile)


