# vectorcast_azure

Integration between VectorCAST and Microsoft Azure DevOps Pipeline

# Installation

This repository uses a git submodule so make sure when you clone this repository, clone with _--recurse-submodules_ option

# Summary

This integration allows the user to execute
[VectorCAST](http://vector.com/vectorcast) Projects in Azure

Results can be published in the following formats
* Coverage results to **_Azure_** and **_SonarQube_**: **_Cobertura_** (xml_data/cobertura)
* Test Results
    * To **_Azure_**: **_JUnit_** (xml_data/junit)
    * To **_SonarQube_**: **_CppUnit_** (xml_data/sonarqube) 

:warning: Due to the limiations of Cobertura plugin, only Statement and Branch results are reported

Two YAML CI files are provided:

- linux/windows_execute.azure-ci.yml - Parallel/Serial build-execute of a VectorCAST Project with options of result output format 

# Calling Action

The python scrip `vcast_exec.py` is the main driver for build/execute VectorCAST Projects.  You can run environments in parallel by specifying `--jobs #`

The api for vcast_exec.py follows:

```
    usage: vcast_exec.py [-h] [--build-execute] [--build | --incremental]
                         [--output_dir OUTPUT_DIR] [--html_base_dir HTML_BASE_DIR]
                         [--cobertura] [--junit] [--sonarqube]
                         [--pclp_input PCLP_INPUT]
                         [--exit_with_failed_count [EXIT_WITH_FAILED_COUNT]]
                         [--aggregate] [--metrics] [--jobs JOBS] [--ci] [-l LEVEL]
                         [-e ENVIRONMENT] [--gitlab | --azure] [--print_exc]
                         [--timing] [-v]
                         ManageProject

    positional arguments:
      ManageProject         VectorCAST Project Name

    optional arguments:
      -h, --help            show this help message and exit

    Script Actions:
      Options for the main tasks

      --build-execute       Builds and exeuctes the VectorCAST Project
      --build               Only builds the VectorCAST Project
      --incremental         Use Change Based Testing (Cannot be used with --build)

    Metrics Options:
      Options generating metrics

      --output_dir OUTPUT_DIR
                            Set the base directory of the xml_data directory.
                            Default is the workspace directory
      --html_base_dir HTML_BASE_DIR
                            Set the base directory of the html_reports directory.
                            The default is the workspace directory
      --cobertura           Generate coverage results in Cobertura xml format
      --junit               Generate test results in Junit xml format
      --sonarqube           Generate test results in SonarQube Generic test
                            execution report format (CppUnit)
      --pclp_input PCLP_INPUT
                            Generate static analysis results from PC-lint Plus XML
                            file to generic static analysis format (codequality)
      --exit_with_failed_count [EXIT_WITH_FAILED_COUNT]
                            Returns failed test case count as script exit. Set a
                            value to indicate a percentage above which the job
                            will be marked as failed

    Report Selection:
      VectorCAST Manage reports that can be generated

      --aggregate           Generate aggregate coverage report VectorCAST Project
      --metrics             Genenereate metrics reports for VectorCAST Project
      --fullstatus          Genenereate full status reports for VectorCAST Project

    Build/Execution Options:
      Options that effect build/execute operation

      --jobs JOBS           Number of concurrent jobs (default = 1)
      --ci                  Use Continuous Integration Licenses
      -l LEVEL, --level LEVEL
                            Environment Name if only doing single environment.
                            Should be in the form of compiler/testsuite
      -e ENVIRONMENT, --environment ENVIRONMENT
                            Environment Name if only doing single environment.
      --gitlab              Build using GitLab CI (default)
      --azure               Build using Azure DevOps

    Script Debug :
      Options used for debugging the script

      --print_exc           Prints exceptions
      --timing              Prints timing information for metrics generation
      -v, --verbose         Enable verbose output
```

# Change log
9/2024
* Added option to generate a --fullstatus report

5/2024
* Merged GitLab and Azure integrations
    * Added flag to fail job if unit tests fail (or above a certain percent)
    * Added flag to process PC-lint Plus XML data into JSON format for GitLab codequality
        * Code Quality metrics will be seen in the Merge Request when both branches contain codequality reports
* Added creating an index.html that will have all the HTML docs listed

    
1/2024
* Updated documentation and examples

11/2023
* Merged GitLab and Azure integrations

10/2023:
* Removed unused scripts
* Migrated actions for VectorCAST into one script git_exec.py (see below for api)
* Added SonarQube test results output format (CppUnit) using `--sonarqube`
* Moved results into individual directories under xml_data:
    * xml/cobertura
    * xml/junit
    * xml/sonarqube
* Fixed cobertura pathing issues

# Licensing Information

The MIT License

Copyright 2020 Vector Informatik, GmbH.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

