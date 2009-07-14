:: Create an executable using py2exe then
:: Make the installer using NSIS

@COLOR 02
:: clean up before starting
@DEL *.exe
@COPY setup.* ..
@CD ..
@DEL *.exe
@DEL *.pyc
@RD dist /s /q
@RD build /s /q

:: Launch the PYTHON setup
C:\PYTHON26\PYTHON.EXE setup.py py2exe

:: Few seconds delay to show dependencies
@COLOR F0
@ECHO.
@PING 1.1 /n 2 > NUL
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
"%ProgramFiles%\NSIS\makensis.exe" setup.nsi
@Echo.

:: clean up at the end
@MOVE *.exe installer
@Echo.
@PAUSE
@DEL setup.* /q
@RD build /s /q
@RD dist /s /q
