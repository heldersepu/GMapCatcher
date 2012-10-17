
This is readme file for wmobilemaps.
author: standa31415
date: 2011/01/16


MD5Sums:
97a1bb40c5ddb2855a0db9ba6431fdd3  wmobilemaps_distr__20110116.zip
c6347abadb33a964beaa751ce377bb8a  wmobilemaps_src__20110116.zip

My intention is to distribute it under GPL.

Few notices / known issues:

Im using the tool while on trips/treks to mountains. As far as I can tell GPS is accurate.


WMobileMaps:
- device doesn't work with online access. All tiles displayed in the device must be downloaded/cached in tiles repository before repository is copied to the device.
- supported repos types - SQLite3 and Files. Recommend SQLite3 because storage card is not filled with lot of small image files.

Available options / features:
- there are 6 buttons on the screen: zoom+ (num+), zoom- (num-), double size (o), lock GPS (G), show GPS state (P), waypoints (W)
- double size - resizes map 2x. It shows whats on the screen but twice as big. I have device with so high PPI, that names in the map are almost not readable. 2x shows everything twice in size.
- lock GPS - when GPS is on and device knows it's position the button is (usually) light blue. After selecting it turns blue and the current GPS position is centered on the map on device. Whenever map is panned it is centered by itself on next GPS update.
- show GPS state - GPS status is displayed. Whether GPS is on/off, lat, lon and number of satellites found
- waypoints - shows dialog window WayPoints. See section "Dialog Window WayPoints" below.

Moving around - touch interface
- use dragging to move around
- press (click) on map somewhere on the display. The place will be moved to the center of the map

Menu 'Options'
- Switch GPS On / Off
- Select Map - selects another map repository (repositories are in '<storage card>\wmgooglemaps\maps\'). Name of the directory with map repository is considered 'map name'.
- Show / Hide GPS coords - shows GPS coords for the middle of the screen
- Save GPS coord - see section "Dialog Window Save GPS Coord" below. 
- Landscape / Portrait - switches screen orientation
- layer 1, layer 2,... - each layer in tiles repository has its own item here. Selecting it, layer is displayed. The names of layers are not displayed correctly. For examlpe it show Google map for layer that is Yahoo map.


Dialog Window "WayPoints"
In fact the window provides 2 functionalities.
- show stored waypoints on the map
- go to selected waypoint

- show stored waypoints on the map
There are 3 radio buttons at the top of the window followed by button "OK". There are zero or more checkboxes below.
By selecting one of radio buttons at the top of the window user chooses whether any stored waypoints should be displayed in the map.
. None means none :)
. All means all :)
. Selected - if the option is selected only selected categories of waypoints will be displayed on the map.
Each category of waypoints has one check box displayed below radio buttons. Check categories which may be displayed.

- go to selected waypoint
At the bottom of the window there are two widgets - combo box populated with stored waypoints and button Go.
To center map on the stored waypoint select waypoint from the list and press Go.


Dialog Window "Save GPS Coord"
Window shows up when user selects "Save GPS Coord" from menu "Options".
It provides a way to adjust details of the waypoint to be stored.
. Coordinates are populated by coordinates of the center of the map
. Time is set to current timestamp
. Tp means - waypoint type. It sets user specified category of the waypoint. (See "- show stored waypoints on the map"). Currently it can be set to single character (letter or number).
. Name - name of the waypoint displayed on the map. If not set current time is used instead.
. Note - stores some more information connected to the waypoint. This information is not displayed anywhere in the application. Only way how to see it is by viewing waypoints file in some text editing tool.
. Color - color used while waypoint is displayed in the map.


Supported systems:
- Windows Mobile 6.5
- Windows Mobile 6.0 (maybe)
I have HTC with Windows Mobile 6.5. Don't have opportunity to test on any other device.

Installation:
- unzip 'wmobilemaps_distr__20110116.zip' and copy 'wmobilemaps' to the storage card.
- if you don't like the name, rename the directory
- start 'wmobilemaps.exe'
- device asks if you really want to run this file
- map 'world' is part of the distribution. It has tiles of the world in maps and sattelite layers with zoom levels 17 and 16. Any other zoom level shows 'missing tile'

Adding new map:
- in gmapcatcher look at 'settings' at 'Custom Maps Directory'. Copy the directory to the storage card to the directory '<storage card>\wmobilemaps\maps\' and start wmobilemaps.
- in menu 'Options' select 'Select map'. New map should be listed in the window.
- when new map is first time opened/selected or map was updated and copied to the device and it is SQLite3 type it can take some time before map is displayed. Device looks like it does nothing and seems to be frozen. It is not. 
Why? Because device scans over all tiles in repository and try to find all different layers used. It can take several minutes. For repository 400MB expect to wait up to 2min. After scan finishes information about repository (number of layers and repository size in bytes) is saved into cache file in maps directory. When the map is opened afterwards the information is read from the cache file and start is fast.



Known issues -  bugs:

- on some occasion while GPS is switched off the app hangs. It stops responding. 
Solution: the only successful solution is to restart device :(
I believe it is deadlock. The code is based on windows mobile example. I think I know where the problem is but i'm not sure and I have no dev environment. For me it is the most annoying error but I am unable to fix it right now.

- on some occasion while panning/zooming wmgooglemaps is not able to open tile because OutOfMemory error. Just close the error message and pan map, the tile should be opened correctly on next occasion. In my case it always is.

- it happened that data for some tile was downloaded incorrectly. So image itself stored in tiles repository is invalid. It happened to me only twice on really slow internet connection. I think problem was with internet connection and not gmapcatcher but I am not sure and I'm unable to reproduce the state. While displaying the tile in gmapcatcher it was half black. Top of tile was OK, but bottom half was black, data were missing. GMapCatcher had no problem processing data but wmgooglemaps has problem. It shows error repeatedly. I was able to get rid of error by trying to close error message and switch the zoom layer. It seems there is problem with image library used by wmgooglemaps (windows mobile?). To get rid of error it is required to re-download the tile.

- waypoints file is not compatible with GMapCatcher. This inconsistency (GMapCatcher / wmgooglemaps) should be solved in next versions.


The end of readme.txt

