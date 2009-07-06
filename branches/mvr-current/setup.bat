:: Create an executable using py2exe then
:: Make the installer using NSIS

@COLOR 02
:: clean up before starting
@DEL *.exe
@DEL *.pyc
@RD dist /s /q
@RD build /s /q

:: Launch the PYTHON setup
C:\PYTHON26\PYTHON.EXE setup.py py2exe

:: Few seconds delay to show dependencies
@COLOR F0
@ECHO.
@PING 1.1 > NUL
@COLOR 03

:: Copy individual files
@COPY missing.png dist
@COPY marker.png dist

:: Need to copy the [etc, lib, share] directories from your GTK+ install (not the pygtk install) to the "dist" dir py2exe created.
:: All the Required files should be in the "common" folder
@XCOPY /E common\* dist

:: Launch the NSIS setup
@COLOR 07
"%programfiles%\NSIS\makensis.exe" setup.nsi

@Echo.
@PAUSE
:: clean up at the end
@RD build /s /q
@RD dist /s /q

