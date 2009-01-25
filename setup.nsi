; The name of the installer
Name "gmapcatcher"

; The file to write
OutFile "gmapcatcher.exe"

; Set the compression algorithm 
SetCompressor /FINAL /SOLID lzma
SetCompressorDictSize 32

; The default installation directory
InstallDir $PROGRAMFILES\gmapcatcher

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\gmapcatcher" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------
; Pages
Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

ShowInstDetails show
ShowUninstDetails show

;--------------------------------
; The stuff to install
Section "gmapcatcher (required)"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put files here
  File /r "dist\*.*"
    
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\gmapcatcher "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gmapcatcher" "DisplayName" "gmapcatcher"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gmapcatcher" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gmapcatcher" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gmapcatcher" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
  ;Microsoft Visual C++ 2008 Redistributable in Quiet mode
  ExecWait '"$INSTDIR\vcredist_x86.exe" /q'
  
SectionEnd

; Optional Shortcuts sections (can be disabled by the user)
Section "Start Menu Shortcuts"
  CreateDirectory "$SMPROGRAMS\gmapcatcher"
  CreateShortCut "$SMPROGRAMS\gmapcatcher\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\gmapcatcher\gmapcatcher.lnk" "$INSTDIR\maps.exe" "" "$INSTDIR\maps.exe" 0
SectionEnd

Section "Desktop Shortcut"
  CreateShortCut "$DESKTOP\gmapcatcher.lnk" "$INSTDIR\maps.exe" "" "$INSTDIR\maps.exe" 0
SectionEnd

Section "Quick Launch Shortcut"
  CreateShortCut "$QUICKLAUNCH\gmapcatcher.lnk" "$INSTDIR\maps.exe" "" "$INSTDIR\maps.exe" 0
SectionEnd

;--------------------------------
; Uninstaller
Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\gmapcatcher"
  DeleteRegKey HKLM SOFTWARE\gmapcatcher

  ; Remove directories used
  RMDir /r "$SMPROGRAMS\gmapcatcher"
  RMDir /r "$INSTDIR"
  
  ;Delete Shortcuts
  Delete "$DESKTOP\gmapcatcher.lnk"
  Delete "$QUICKLAUNCH\gmapcatcher.lnk"

SectionEnd
