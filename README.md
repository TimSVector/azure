# vectorcast_azure

Initial Integration Between VectorCAST and Microsoft Azure DevOps Pipeline

# Summary

This integration allows the user to execute
[VectorCAST](http://vector.com/vectorcast) Projects in Azure

Results are published in **_Junit_** and **_Cobertura_**

:warning: Due to the limiations of Cobertura plugin, only Statement and Branch results are reported

Four YAML CI files are provided:

- linux/windows_serial_build_execute.azure-ci.yml   - Serial build-execute of a VectorCAST Project 
- linux/windows_parallel_build.azure-ci.yml         - Parallel build and serial execute of a VectorCAST Project 


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

