<font size='5'><b>User guide for GMapCatcher (trunk)</b></font>


# Overview #

GMapCatcher is an online and offline map viewer. Currently the following map providers are supported:
  * [CloudMade](http://maps.cloudmade.com/)
  * [OpenStreetMap](http://www.openstreetmap.org/)
  * [Google Maps](http://maps.google.com/) No longer supported, see [Issue 210](https://github.com/heldersepu/GMapCatcher/issues/210)
  * [Yahoo](http://maps.yahoo.com/)
  * [InformationFreeway](http://www.informationfreeway.org/)
  * [OpenCycleMap](http://www.opencyclemap.org/)
  * [Google Map Maker](http://www.google.com/mapmaker)
  * [Virtual Earth](http://www.bing.com/maps/)

Users can choose their preferred map and watch it while online. All viewed map section will be stored on disk and may be viewed offline. Additionally a downloading tool is provided which saves a user defined area to disk for offline viewing.

# User interface #

After starting the programme the GUI shows the map, a small size scroll bar on the left and a toolbar on top.

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/main_window.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/main_window.png)

By using the scroll bar the resolution/scale of the map can be changed. The toolbar consists of two rows and offers the following actions and settings (first row to second row, left to right):
  * **Main configuration button**
> Pressing the button opens a drop down menu with 5 configuration categories. Choosing one of them opens the complete programme setup where the chosen category is active. In addition there is the 'Save Path Maps' Menu item that makes the visual path download tool visible; see the description of the visual path download for details

  * **Drop down menu/edit field for new and stored locations**
> By using the drop down menu one of the stored locations is selected. By entering text a place with this name is searched (currently only available if online).

  * **Confirmation button**
> Confirms entered text in drop down menu/edit field (alternative to pressing 'ENTER' in edit field).

  * **Check box to indicate working mode (online or offline)**

  * **Check box to indicate force update facility**

  * **GPS mode -button (only if GPS in enabled)**

  * **Drop down menu for map type selection**
  * If "one directory per map" is **not** selected, one of four map types (Map, Terrain, Satellite, Hybrid) can be selected, depending on map used.
  * If "one directory per map" **is** selected, map service can be selected.

## Right mouse click ##

While displaying a map a right mouse click opens the following menu:

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/gmap_rclick.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/gmap_rclick.png)

The first four items change the map section display and explain themselves:
  * Zoom In: Decrease zoom
  * Zoom Out: Increase zoom
  * Center map here: Position of cursor becomes centre of map.
  * Reset: Display map with highest zoom level.

Actions of the next three items:
  * Batch Download: See description [Download](https://github.com/heldersepu/GMapCatcher/blob/wiki/User_Guide.md#download)
  * [Export Map](https://github.com/heldersepu/GMapCatcher/blob/wiki/User_Guide.md#export-map-to-image): Open dialog to save current display of map to file 'map.png' in home folder
  * Add Marker: Add a marker at position of cursor (description of marker must be done afterwards by using the main configuration menu)

Actions of the final 2 items:
  * Copy Location: copy mouse location of right-click to the clipboard
  * Copy GPS: copy GPS location to the clipboard
> you may then paste locations from the clipboard as needed

## Visual path download ##
> When the visual path download tool is visible, it describes the area that would be included in a visual download.

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/visual_download.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/visual_download.png)

  * Shift+Scroll changes the size of the area
  * Ctrl+Scroll changes the minimum zoom level to download

> When you **Shift+drag** the map, then the area included in the visual download zone is queued for download, from the zoom level below the current view zoom level, to the visual download's minimum zoom level as set

> One main function of the tool is to allow you to download close-up maps along a path; it gives feedback of the number of tiles downloaded/requested while downloading


## Drawing paths ##

Paths in GMapCatcher can be used to measure distances and draw paths to follow while navigating.

You can start drawing a path by pressing F7. This activates the ruler and you can left-click on any point of the map to add a point to the path.

If you make a mistake, press delete to remove last point. You can zoom and move map normally when creating a path.

The path shows segment length and the whole path length (up to that point) on every point of the path. After you finish drawing the path, just press F7 again to close the tool. You then have a choice to use path as a track or dismiss it. If you choose to use it as track, it will be shown on the map until you close GMapCatcher or hide the track through Track control.

# Tools menu #
## Operations ##

### Download ###
![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/GMapCatcher_tools.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/GMapCatcher_tools.png)

Within the following dialog an area and a zoom level to download a map section can be entered. The dialog stays alive during the download.

> ![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/download_window.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/download_window.png)

The centre of the downloaded area is defined by entering latitude and longitude. The size of the area by entering width and height. The maximum and minimum zoom level define the scale of the downloaded map tiles. The map type which is set in the drop down menu for 'map type selection' is used for the download.

> Action of buttons in bottom line of window:
    * left button: Start download
    * by right-clicking Start download, you can select the map layers to download.
    * middle button: Open menu to restart/continue a previous download
    * right button: Pause current download.

> How to update and/or modify a downloaded area? If you have e.g. downloaded the complete US with zoom level 4, now you want to update the NY area with zoom level 2, then you open the Download Window, simply enter the coordinates for NY and set the zoom level to 2, the range width and height to 50km and start the download. Now the NY area is updated the rest remains the same and the complete US is still available for offline viewing with zoom level 4 while NY is available with zoom level 2.

### Export map to image ###
You can save current display of map to file
![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/export_map.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/export_map.png)

The image will be saved in your installation directory:
C:\Program Files (x86)\GMapCatcher

### Export Repo tiles ###
You can export your downloaded map tiles from one format to another

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/export_window.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/export_window.png)

### Track control ###
Track control allows controlling of tracks shown in the map. Through this window you can also import and export tracks, as well as export GPS track. GMapCatcher uses GPX-files to store this information.

Toggling the tracks also toggles the tracks shown on the map.

With import tracks you can import tracks and routes from GPX-files. You can export selected tracks to a GPX-file with "Export selected tracks" -button. Note that this exports all the selected tracks to a single file, so if you want to export them seperately, select only one track at a time. By selecting "Export GPS track" you can export the current GPS-trace to GPX-file (only available if GPS and GPS-track drawing is active).

Below is Track control window being used to show one of the drawn ruler paths and one track from imported file.

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/track_control.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/track_control.png)

### GPS window ###
GPS window shows the current GPS information, if available. Unit of speed is determined by unit selection in [User\_Guide#Settings](User_Guide#Settings.md).

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/gps_window.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/gps_window.png)

# Settings #

<a href='Hidden comment: 
I guess this is pretty much wrong information by now?

All values in the tab Settings describe display properties when starting the programme. Therefore any change requires a restart of the programme in order to have effect.
'></a>

## Main ##

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_main.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_main.png)

  * 'Size' defines the display size of the GMapCatcher window. 'Zoom' defines the zoom level of the map section specified by the coordinates of the field 'Center', which is displayed on start up.
  * The button 'Use Currents' sets all values according to the current display.

  * 'Select units' determines the units shown on all of the map components. These include track lengths, GPS speed, map scale etc.
  * 'Start offline' sets whether to go online or offline at start.
  * 'Close settings' sets behaviour when closing the program. If 'Save view params' is set, the window location and size will be saved.
  * 'Location Status' sets statusbar type. Type can be one off 'Off', 'Mouse' or 'GPS'.
  * 'Custom maps directory' sets where to save maps and in what format.

## Edit locations ##

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_locations.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_locations.png)

Allows adding, deleting and editing of locations. All locations searched will be added here.

## Edit markers ##

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_markers.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_markers.png)

Allows adding, deleting and editing of markers. You can add marker also by CTRL + left-clicking the map in the point where you want marker.

## Change Theme ##

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_theme.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_theme.png)

  * 'Mark center of the map' allows adding a center point to the map window.
  * 'Map scales' selects whether to draw map scale
  * 'Map service' allows selecting of map service.
    * 'Use different folder per map service' allows using multiple maps without them interfering with each other. Also, when selected, map selection box in main window shows all the available map services instead of showing just map layers of selected map.
    * 'Select map servers' allows toggling displaying of the maps in map selection. You can disable map by entering 0 to 'status' and enable by entering '1'

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_map_servers.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_map_servers.png)

## GPS Options ##

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_gps.png](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/images/settings_gps.png)

  * 'GPS' allows setting of GPS behaviour
    * 'GPS type' selects GPS type, possible choices are 'Off', 'GPSd' and 'Serial'.
      * 'GPSd' connects to GPSd running on localhost (might change in future versions to allow for remote GPSd also).
      * 'Serial' connects straight to NMEA-compatible GPS-device connected to serial (COM) -port.
    * 'GPS update rate in seconds' allows selecting of GPS update rate
      * Determines how often the GPS location is set on map
      * Lower values use more CPU and also affect the flickering of tracks etc.
    * 'Maximum zoom for GPS' sets maximum zoom to show GPS on. On zoom levels higher than this, GPS marker isn't shown and the map won't recenter.
    * 'Initial GPS mode' determines the GPS mode when starting GMapCatcher

  * 'GPS track' allows drawing of GPS track
    * 'Track width' sets the width of the track drawn. **Also affects rulers and tracks!**
    * 'Point interval' sets the minimum distance from last point before adding a new one
      * Values over 50 meters are recommended, as every point uses memory (72 bytes to be exact) and memory usage can grow very high on long trips otherwise.

  * 'Serial' sets the serial port parameters for GPS

# Keyboard shortcuts #

## General ##
| **Shortcut Key** | **Description** |
|:-----------------|:----------------|
|  F1              |  Open help page |
|  F2              |  [Export map to image](https://github.com/heldersepu/GMapCatcher/blob/wiki/User_Guide.md#export-map-to-image) |
|  F3              |  Toggle GPS window |
|  F4              |  Import markers from KML file |
|  F5              |  Refresh        |
|  F6              |  Hide/Show the visual path download zone |
|  F7              |  Draw a path in the map |
|  F8              |  Show the path control window |
|  F9              |  Hide/Show the markers |
|  F12             |  Hide/Show all buttons |
|  F11             |  Full screen    |
|  ESC             |  Undo F12 & F11 |
|  Ctrl + Click    |  Add marker     |
|  Alt + 2Click    |  Zoom out       |
|  2Click          |  Zoom in        |
|  Ctrl + W        |  Closes the current window |
|  Ctrl + Q        |  Quits gmapcatcher from the main window |
|  Ctrl + S        |  Saves current page of config settings from config window |



&lt;BR&gt;


## Navigation (only after hiding buttons F12) ##
| **Shortcut Key** | **Description** |
|:-----------------|:----------------|
|  Arrow Keys      |  Pan Left, Right, Up and Down |
|  +               |  Zoom in        |
|  -               |  Zoom out       |
|  Page Up         |  Pan wider Up   |
|  Page Down       |  Pan wider Down |
|  Home            |  Pan wider Left |
|  End             |  Pan wider Rigth |
|   M              |  Show Map Layer |
|   S              |  Show Satellite Layer |
|   T              |  Show Terrain Layer |
|   H              |  Show Hybrid Layer |




&lt;BR&gt;


## GPS related (only when GPS is enabled) ##
| **Shortcut Key** | **Description** |
|:-----------------|:----------------|
|  Space           |  Re center GPS cursor |


# Config File #
The config file is named **gmapcatcher.conf** and it contains all the settings for GMapCatcher.

Details of all the keys in the config file here:
https://github.com/heldersepu/GMapCatcher/blob/master/gmapcatcher/mapConf.py#L112
