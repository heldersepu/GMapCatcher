!define PRODUCT_NAME "ASMS_Map"
!define PRODUCT_VERSION "1.3.1.0"
!define PRODUCT_WEB_SITE "http://www.aleppoltd.com/"
!include nsDialogs.nsh

; The name of the installer
Name "${PRODUCT_NAME}"

; The file to write
OutFile "${PRODUCT_NAME}.${PRODUCT_VERSION}.exe"

; Set the compression algorithm
SetCompressor /FINAL /SOLID lzma
SetCompressorDictSize 32

; The default installation directory
InstallDir "C:\GPS\ASMS"

; Registry key to check for directory (so if you install again, it will
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\${PRODUCT_NAME}" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------
;Version Information
VIProductVersion "${PRODUCT_VERSION}"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "Comments" ""
VIAddVersionKey "LegalCopyright" "${PRODUCT_WEB_SITE}"
VIAddVersionKey "FileDescription" "Offline Map Viewer"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"

;--------------------------------
; Pages
Page components
;Page directory
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
	${NSD_CreateLabel} 75u 30u 80% 8u "ASMS Map was succesfully installed on your computer."
	Pop $0
	${NSD_CreateCheckbox} 80u 50u 50% 8u "Run ASMS Map v${PRODUCT_VERSION}"
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
    Delete "$INSTDIR\DNSAPI.DLL"
    ${If} $boolCHECKBOX != "False"
        Exec "$INSTDIR\maps.exe"
    ${EndIf}
FunctionEnd

;--------------------------------
; The final uninstall page that asks to remove all images
Function un.finalPage

	nsDialogs::Create 1018
	Pop $0
	${NSD_CreateLabel} 50u 30u 80% 8u "ASMS Map was uninstalled from your computer."
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
        RMDir /r "$PROFILE\.ASMS"
    ${EndIf}
FunctionEnd

;--------------------------------
; The stuff to install
Section "${PRODUCT_NAME} (required)"
    ;SetAutoClose true
    SectionIn RO
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

    ; Check if VC++ 2008 runtimes are already installed:
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{FF66E9F6-83E7-3A3E-AF14-8DE9A809A6A4}" "DisplayName"
    ; If VC++ 2008 runtimes are not installed execute in Quiet mode
    StrCmp $0 "Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022" +2 0
        ExecWait '"$INSTDIR\vcredist_x86.exe" /q'
        
    CreateDirectory "$PROFILE\.ASMS"
    Rename "$INSTDIR\.ASMS\*.*" "$PROFILE\.ASMS"
    CopyFiles /SILENT "$INSTDIR\.ASMS\*.*" "$PROFILE\.ASMS" 1024
SectionEnd

Section "Desktop Shortcut"
    SectionIn RO
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\maps.exe"
SectionEnd


;--------------------------------
; Uninstaller
Section "Uninstall"
    SetAutoClose true
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
    DeleteRegKey HKLM "SOFTWARE\${PRODUCT_NAME}"

    ; Remove directories used
    RMDir /r "$INSTDIR"

    ; Delete Shortcuts
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
SectionEnd
