:: Make a "tiles" installer using NSIS

@SET NSI_NAME=setupTiles.nsi
@SET NSIS=%PROGRAMFILES%\GMapCatcher\NSIS\makensis.exe
@SET FILE_NAME=MyMaps.exe
@SET FOLDER_PATH=%USERPROFILE%\.googlemaps

@TITLE Export Maps
@COLOR F0

@IF NOT EXIST "%NSIS%" GOTO ERROR
@IF NOT EXIST "%NSI_NAME%" GOTO ERROR
@IF NOT EXIST "%FOLDER_PATH%" GOTO ERROR

    @ECHO.
    @ECHO.
    @ECHO.
    @ECHO      This tool will export all your downloaded maps and locations,
    @ECHO     it creates a self-extracting exe in your desktop (%FILE_NAME%)
    @ECHO.   
    @ECHO.   
    @ECHO   ** if you DO NOT WISH TO PROCEED please close this window now **
    @ECHO.
    @ECHO.
    @ECHO.
    @PAUSE

    COPY "%NSI_NAME%" "%FOLDER_PATH%\%NSI_NAME%"
    CD "%FOLDER_PATH%"
    CALL "%NSIS%" "%NSI_NAME%"
    @MOVE "%FILE_NAME%" "%USERPROFILE%\Desktop"
    @DEL "%FOLDER_PATH%\%NSI_NAME%"

:SUCCESS
@ECHO.
@ECHO  File created on your desktop
@ECHO.
@GOTO EOF

:ERROR
@ECHO.
@ECHO  Required Files or Folders not found!
@ECHO.

:EOF
@PING 1.1 -n 8 > NUL
