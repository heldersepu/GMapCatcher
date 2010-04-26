WindowsMobileGooglemaps = wmgooglemaps

- ShowPicture = source code
- wmgooglemaps.zip = binary files

*) ShowPicture:
 To use GPS following "how-to" was used: http://msdn.microsoft.com/en-us/windowsmobile/cc719033.aspx
Compiled dll from the sample project described in the "How-To" is required to correctly run the application (= "dll source"). "dll source" for the GPS dll is part of the windows mobile 6 SDK and in the "how-to" guy seys - one can freele use the sample. I'm not appending the the source code of "dll source". Because if anybody wants to compile the wmgooglemaps must have WinMobile6SDK so it has "dll source".

*) wmgoogleaps.zip:
compiled binary files. I don't know if it is OK to distribute them. Im including them for your personal purpose - if you want to see the app running, it's enough to copy structure to the storage card and put storage card into the WinMobile device. Browse to the folder and run wmgooglemaps

*) dir structure:
- in the root directory of the storage card create directory wmgooglemaps
- put files in it (Microsoft.WindowsMobile.Samples.Location.dll, wmgooglemaps.exe, missing.png)
- any other directory is considered maps directory.
- after app is run some files are created - for example the last GPS position of displayed on the display
- if the files doesn't exist while first run, disgusting exception is displayed, but it should be ok.

*) When GPS is switched off sometimes happens that app frozes. It seems there is some problem with the thread synchronisation, but no sure where. Didn't expected it in the detail.


Standa.
