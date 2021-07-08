set path=%VECTORCAST_DIR%\mingw\bin;%PATH%
if exist managerDriver.exe del managerDriver.exe

rem This compile command builds an executable that needs stdin
gcc -g manager_driver.c manager.c database.c whitebox.c -o managerDriver.exe || exit 1

rem This compile command builds an executable that does not need stdin
rem gcc -g -DORDER manager_driver.c manager.c database.c whitebox.c -o managerDriver.exe || exit 1
