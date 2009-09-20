:: Create an executable using py2exe then
:: Make the installer using NSIS

:: Tested with:
::  python-2.6.2.msi
::  gtk2-runtime-2.14.7-2009-01-13-ash.exe
::  gtk2-themes-2008-10-22-ash.exe
::  py2exe-0.6.9.win32-py2.6.exe
::  pycairo-1.4.12-2.win32-py2.6.exe
::  pygobject-2.14.2-2.win32-py2.6.exe
::  pygtk-2.12.1-3.win32-py2.6.exe
::  nsis-2.45-setup.exe
::  AccessControl.zip


@COLOR 02
:: clean up before starting
@DEL *.exe
@COPY setup.* ..
@CD ..
@DEL *.exe
@DEL *.pyc /s
@RD dist /s /q
@RD build /s /q

:: Launch the PYTHON setup
C:\PYTHON26\PYTHON.EXE setup.py py2exe

:: Few seconds delay to show dependencies
@COLOR F0
@ECHO.
@PING 1.1 /n 2 /i 1 > NUL
@COLOR 03

:: Copy all the image files
@MD dist\images
@COPY images dist\images

:: Need to copy the [etc, lib, share] directories from your GTK+ install 
::(not the pygtk install) to the "dist" dir py2exe created.
:: All the Required files should be in the "common" folder
@XCOPY /E common\* dist

:: Launch the NSIS setup
@COLOR 07
SET NSIS="%ProgramFiles%\NSIS\makensis.exe"
IF NOT EXIST %NSIS% SET NSIS="%ProgramFiles(x86)%\NSIS\makensis.exe"
CALL %NSIS% setup.nsi
@ECHO.

:: clean up at the end
@DEL *.pyc /s
@MOVE *.exe installer
@ECHO.
@PAUSE
@DEL setup.* /q
@RD build /s /q
@RD dist /s /q
