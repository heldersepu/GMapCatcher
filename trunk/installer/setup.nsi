!define PRODUCT_NAME "GMapCatcher"
!define PRODUCT_VERSION "0.7.5.0"
!define PRODUCT_WEB_SITE "http://code.google.com/p/gmapcatcher/"
!include nsDialogs.nsh

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
VIProductVersion "${PRODUCT_VERSION}"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "Comments" "GMapCatcher is an offline map viewer. It downloads map tiles automatically, display them using a specific GUI. User can view maps offline."
VIAddVersionKey "LegalCopyright" "${PRODUCT_WEB_SITE}"
VIAddVersionKey "FileDescription" "Offline Map Viewer"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"

;--------------------------------
; Pages
Page components
Page directory
Page instfiles
Page custom finalPage

UninstPage uninstConfirm
UninstPage instfiles
UninstPage custom un.finalPage

ShowInstDetails show
ShowUninstDetails show

Var CHECKBOX
Var boolCHECKBOX
Var Image
Var ImageHandle

;--------------------------------
; The final install page that asks to run the application
Function finalPage

	nsDialogs::Create 1018
	Pop $0
	${NSD_CreateLabel} 75u 30u 80% 8u "GMapCatcher was succesfully installed on your computer."
	Pop $0
	${NSD_CreateCheckbox} 80u 50u 50% 8u "Run GMapCatcher v${PRODUCT_VERSION}"
	Pop $CHECKBOX
    SendMessage $CHECKBOX ${BM_SETCHECK} ${BST_CHECKED} 0
    GetFunctionAddress $1 OnCheckbox
	nsDialogs::OnClick $CHECKBOX $1

    ; Add an image
    ${NSD_CreateBitmap} 0 0 100% 40% ""
    Pop $Image
    ${NSD_SetImage} $Image "$INSTDIR\images\setup.bmp" $ImageHandle
	nsDialogs::Show
    ${NSD_freeImage} $ImageHandle

FunctionEnd
Function OnCheckbox
    SendMessage $CHECKBOX ${BM_GETSTATE} 0 0 $1
    ${If} $1 != 8
        StrCpy $boolCHECKBOX "True"
    ${Else}
        StrCpy $boolCHECKBOX "False"
    ${EndIf}
FunctionEnd
Function .onInstSuccess
	${If} $boolCHECKBOX != "False"
        Exec "$INSTDIR\maps.exe"
    ${EndIf}
FunctionEnd

;--------------------------------
; The final uninstall page that asks to remove all images
Function un.finalPage

	nsDialogs::Create 1018
	Pop $0
	${NSD_CreateLabel} 50u 30u 80% 8u "GMapCatcher was uninstalled from your computer."
	Pop $0
	${NSD_CreateCheckbox} 60u 50u 50% 8u "Remove all downloaded images"
	Pop $CHECKBOX
    GetFunctionAddress $1 un.OnCheckbox
	nsDialogs::OnClick $CHECKBOX $1
	nsDialogs::Show

FunctionEnd
Function un.OnCheckbox
    SendMessage $CHECKBOX ${BM_GETSTATE} 0 0 $1
    ${If} $1 != 8
        StrCpy $boolCHECKBOX "True"
    ${Else}
        StrCpy $boolCHECKBOX "False"
    ${EndIf}
FunctionEnd
Function un.onUninstSuccess
    ${If} $boolCHECKBOX == "True"
        RMDir /r "$PROFILE\.googlemaps"
    ${EndIf}
FunctionEnd

;--------------------------------
; The stuff to install
Section "${PRODUCT_NAME} (required)"
    SetAutoClose true
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
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\maps.exe" 
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall ${PRODUCT_NAME}.lnk" "$INSTDIR\uninstall.exe" 
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME} Export Maps.lnk" "$INSTDIR\ExportMaps.bat" 
    ; Create a shortcut to the project Homepage
    WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME} Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section "Desktop Shortcut"
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\maps.exe"
SectionEnd

Section "Quick Launch Shortcut"
    CreateShortCut "$QUICKLAUNCH\${PRODUCT_NAME}.lnk" "$INSTDIR\maps.exe"
SectionEnd

;--------------------------------
; Uninstaller
Section "Uninstall"
    SetAutoClose true
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
