Name "GMapCatcher Maps"
OutFile "MyMaps.exe"
InstallDir $PROFILE\.googlemaps

;--------------------------------
;Version Information
  VIProductVersion "0.0.0.0"
  VIAddVersionKey "ProductName" "GMapCatcher"
  VIAddVersionKey "Comments" "GMapCatcher is an offline viewer of google maps. It downloads google-map tiles automatically, display them using a specific GUI. User can view google map offline."
  VIAddVersionKey "LegalCopyright" "http://code.google.com/p/gmapcatcher/"
  VIAddVersionKey "FileDescription" "Maps for GMapCatcher"
  VIAddVersionKey "FileVersion" ""

;--------------------------------
; Pages
Page components
Page instfiles
ShowInstDetails show

Function FileJoin
  !define FileJoin `!insertmacro FileJoinCall`

  !macro FileJoinCall _FILE1 _FILE2 _FILE3
    Push `${_FILE1}`
    Push `${_FILE2}`
    Push `${_FILE3}`
    Call FileJoin
  !macroend

  Exch $2
  Exch
  Exch $1
  Exch
  Exch 2
  Exch $0
  Exch 2
  Push $3
  Push $4
  Push $5
  ClearErrors

  IfFileExists $0 0 error
  IfFileExists $1 0 error
  StrCpy $3 0
  IntOp $3 $3 - 1
  StrCpy $4 $2 1 $3
  StrCmp $4 \ +2
  StrCmp $4 '' +3 -3
  StrCpy $4 $2 $3
  IfFileExists '$4\*.*' 0 error

  StrCmp $2 $0 0 +2
  StrCpy $2 ''
  StrCmp $2 '' 0 +3
  StrCpy $4 $0
  goto +3
  GetTempFileName $4
  CopyFiles /SILENT $0 $4
  FileOpen $3 $4 a
  IfErrors error
  FileSeek $3 -1 END
  FileRead $3 $5
  StrCmp $5 '$\r' +3
  StrCmp $5 '$' +2
  FileWrite $3 '$\r$'

  ;FileWrite $3 '$\r$--Divider--$\r$'

  FileOpen $0 $1 r
  IfErrors error
  FileRead $0 $5
  IfErrors +3
  FileWrite $3 $5
  goto -3
  FileClose $0
  FileClose $3
  StrCmp $2 '' end
  Delete '$EXEDIR\$2'
  Rename $4 '$EXEDIR\$2'
  IfErrors 0 end
  Delete $2
  Rename $4 $2
  IfErrors 0 end

  error:
  SetErrors

  end:
  Pop $5
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0
FunctionEnd

;--------------------------------
Section "My Maps"

  SectionIn RO
  SetOutPath "$PROFILE\.googlemaps"
  File /nonfatal /r "tiles"

SectionEnd

Section "My Locations"

  Var /GLOBAL dPath
  StrCpy $dPath "$PROFILE\.googlemaps"

  SetOutPath "$dPath"
  ; The locations file will be copied as newLoc
  File /nonfatal "/oname=newLoc" "locations"

  ; If the locations file exists append the newLoc
  IfFileExists "$dPath\locations" 0 doRename
    ${FileJoin} "$dPath\locations" "$dPath\newLoc" "$dPath\temp"
    Delete "$dPath\newLoc"
    Delete "$dPath\locations"
    Rename "$dPath\temp" "$dPath\locations"

  doRename:
  IfFileExists "$dPath\newLoc"  0 +2
    Rename "$dPath\newLoc"  "$dPath\locations"

SectionEnd
