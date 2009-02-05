:: Make a "tiles" installer using NSIS

@SET NSI_NAME=setupTiles.nsi
@SET NSIS=%PROGRAMFILES%\gmapcatcher\NSIS\makensis.exe
@SET FILE_NAME=MyMaps.exe
@SET FOLDER_PATH=%USERPROFILE%\.googlemaps

@TITLE Export Maps
@COLOR F0

@IF NOT EXIST "%NSIS%" GOTO ERROR
@IF NOT EXIST "%NSI_NAME%" GOTO ERROR
@IF NOT EXIST "%FOLDER_PATH%" GOTO ERROR
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
