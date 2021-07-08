set path=%VECTORCAST_DIR%\mingw\bin;%PATH%
if exist managerDriver.exe del managerDriver.exe

rem This compile command builds an executable that needs stdin
g++ -g manager_driver.cpp manager.cpp database.cpp whitebox.cpp -o managerDriver.exe || exit 1

rem This compile command builds an executable that does not need stdin
rem g++ -g -DORDER manager_driver.cpp manager.cpp database.cpp whitebox.cpp -o managerDriver.exe || exit 1
