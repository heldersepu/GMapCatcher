:: Create an executable using py2exe then
:: Make the installer using NSIS

:: Tested with:
::  python-2.7.msi
::  gtk2-runtime-2.22.0-2010-10-21-ash.exe
::  gtk2-themes-2009-09-07-ash.exe
::  PIL-1.1.7.win32-py2.7.exe
::  py2exe-0.6.9.win32-py2.7.exe
::  pycairo-1.8.10.win32-py2.7.exe
::  pygobject-2.26.0.win32-py2.7.exe
::  pygtk-2.22.0.win32-py2.7.exe
::  nsis-2.46-setup.exe
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
%SystemDrive%\PYTHON27\PYTHON.EXE setup.py py2exe

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
@DEL *.pyc /s > NUL
@CLS
@COLOR 0A
@MOVE *.exe installer
@ECHO.
@PAUSE
@DEL setup.* /q
@RD build /s /q
@RD dist /s /q
