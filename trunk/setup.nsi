!define PRODUCT_NAME "GMapCatcher"
!define PRODUCT_VERSION "0.080"
!define PRODUCT_WEB_SITE "http://code.google.com/p/gmapcatcher/"

; The name of the installer
Name "${PRODUCT_NAME}"

; The file to write
OutFile "${PRODUCT_NAME}-${PRODUCT_VERSION}.exe"

; Set the compression algorithm
SetCompressor /FINAL /SOLID lzma
SetCompressorDictSize 32

; The default installation directory
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"

; Registry key to check for directory (so if you install again, it will
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\${PRODUCT_NAME}" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------
;Version Information
VIProductVersion "${PRODUCT_VERSION}.0.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "Comments" "GMapCatcher is an offline viewer of google maps. It downloads google-map tiles automatically, display them using a specific GUI. User can view google map offline."
VIAddVersionKey "LegalCopyright" "${PRODUCT_WEB_SITE}"
VIAddVersionKey "FileDescription" "Offline Google Map Viewer"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"

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
Section "${PRODUCT_NAME} (required)"

    SectionIn RO

    ; Set output path to the installation directory.
    SetOutPath $INSTDIR

    ; Put files here
    File /r "dist\*.*"

    ; Write the installation path into the registry
    WriteRegStr HKLM "SOFTWARE\${PRODUCT_NAME}" "Install_Dir" "$INSTDIR"

    ; Write the uninstall keys for Windows
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoRepair" 1
    WriteUninstaller "uninstall.exe"

    ; Change the permissions of the install directory
    AccessControl::GrantOnFile "$INSTDIR" "(BU)" "FullAccess"

    ; Move the ".googlemaps" folder to the %UserProfile% (if it does not already exist)
    ; Change the permissions of the ".googlemaps" folder
    IfFileExists "$PROFILE\.googlemaps\*.*" +3 0
        Rename "$INSTDIR\.googlemaps\*.*" "$PROFILE\.googlemaps"
        AccessControl::GrantOnFile "$PROFILE\.googlemaps" "(BU)" "FullAccess"

    CopyFiles /SILENT "$INSTDIR\.googlemaps\*.*" "$PROFILE\.googlemaps" 1024

    ; Check if VC++ 2008 runtimes are already installed:
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{FF66E9F6-83E7-3A3E-AF14-8DE9A809A6A4}" "DisplayName"
    ; If VC++ 2008 runtimes are not installed execute in Quiet mode
    StrCmp $0 "Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022" +2 0
        ExecWait '"$INSTDIR\vcredist_x86.exe" /q'

SectionEnd

; Optional Shortcuts sections (can be disabled by the user)
Section "Start Menu Shortcuts"
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\maps.exe" "" "$INSTDIR\maps.exe" 0
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall ${PRODUCT_NAME}.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME} Export Maps.lnk" "$INSTDIR\ExportMaps.bat" "" "$INSTDIR\ExportMaps.bat" 0
    ; Create a shortcut to the project Homepage
    WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME} Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section "Desktop Shortcut"
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\maps.exe" "" "$INSTDIR\maps.exe" 0
SectionEnd

Section "Quick Launch Shortcut"
    CreateShortCut "$QUICKLAUNCH\${PRODUCT_NAME}.lnk" "$INSTDIR\maps.exe" "" "$INSTDIR\maps.exe" 0
SectionEnd

;--------------------------------
; Uninstaller
Section "Uninstall"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
    DeleteRegKey HKLM "SOFTWARE\${PRODUCT_NAME}"

    ; Remove directories used
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
    RMDir /r "$INSTDIR"

    ; Delete Shortcuts
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
    Delete "$QUICKLAUNCH\${PRODUCT_NAME}.lnk"

SectionEnd
