@COLOR 02
:: clean up before starting
@DEL *.exe
@CD ..
@DEL *.exe
@DEL *.pyc /s
@DEL *.bak /s
@RD dist /s /q
@RD build /s /q

@ECHO.
@ECHO.
@ECHO  CLEANING COMPLETE!   READY TO START?
@ECHO.
@PAUSE

:: Launch the PYTHON setup
@COPY installer\setup.* .
%SystemDrive%\PYTHON27\PYTHON.EXE setup.py py2exe

@ECHO.
@COLOR 0A
@PAUSE
