## @package src.mapConf
# Read and write to the configuration file

import os
import gtk
import pygtk
import csv
import src.mapGPS as mapGPS
import src.mapUtils as mapUtils
import src.mapTools as mapTools
import src.mapPixbuf as mapPixbuf
import src.ASALTradio as ASALTradio
import src.fileUtils as fileUtils
import src.widMySettings as widMySettings
import src.widASALTsettings as widASALTsettings
import src.widTreeView as treeViewSettings

from src.gtkThread import *
from src.mapConf import MapConf
from src.mapMark import MyMarkers
from src.DLWindow import DLWindow
from src.ASALTWindow import ASALTWindow
from src.ASALTradio import ASALTradio
from src.mapUpdate import CheckForUpdates
from src.mapServices import MapServ
from src.customMsgBox import error_msg
from src.mapDownloader import MapDownloader
from src.customWidgets import lbl, _frame, myToolTip, gtk_menu, FileChooser, _frame
from src.mapConst import *
from src.widDrawingArea import DrawingArea
from src.xmlUtils import kml_to_markers
from os.path import join, dirname, abspath, exists



## Class used to read and save the configuration values
class MapOver():
    #default_text = "Enter location here!"
    update = None
    myPointer = None
    reCenter_gps = False
    markercount = 0

    ## Get the zoom level from the scale
    def get_zoom(self):
        return int(self.scale.get_value())


		## Show the combo list if is not empty
    def combo_popup(self):
        if self.combo.get_model().get_iter_root() is not None:
            self.combo.popup()

    ## Handles the pressing of arrow keys
    def key_press_combo(self, w, event):
        if event.keyval in [65362, 65364]:
            self.combo_popup()
            return True

    ## Handles the events in the Tools buttons
    def tools_button_event(self, w, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            w.popup(None, None, None, 1, event.time)
        elif event.type == gtk.gdk.KEY_PRESS and \
             event.keyval in [65293, 32]:
            self.menu_tools(TOOLS_MENU[0])

    ## Handles the click in the offline check box
    def offline_clicked(self, w):
        self.drawing_area.repaint()
        if not self.cb_offline.get_active():
            self.do_check_for_updates()

    ## Enables drop marker mode
    def drop_marker_mode(self,w):
        print "drop marker enabled"


    ## Start checking if there is an update
    def do_check_for_updates(self):
        if self.conf.check_for_updates and (self.update is None):
            # 3 seconds delay before starting the check
            self.update = CheckForUpdates(3, self.conf.version_url)

    ## Handles the change in the GPS combo box
    def gps_changed(self, w):
        self.gps.set_mode(w.get_active())
        self.drawing_area.repaint()

    ## Handles the change in the combo box Layer(Map, Sat.. )
    def layer_changed(self, w):
        self.layer = w.get_active()
        self.drawing_area.repaint()

    def download_clicked(self, w, pointer=None):
        rect = self.drawing_area.get_allocation()
        if (pointer is None):
            tile = self.drawing_area.center
        else:
            tile = mapUtils.pointer_to_tile(
                rect, pointer, self.drawing_area.center, self.get_zoom()
            )

        coord = mapUtils.tile_to_coord(tile, self.get_zoom())
        km_px = mapUtils.km_per_pixel(coord)
        dlw = DLWindow(coord, km_px*rect.width, km_px*rect.height,
                        self.layer, self.conf.init_path,
                        self.conf.map_service,
                        self.conf.cloudMade_styleID
                    )
        dlw.show()

    ## Validation of the markers
    #  looking for intersections with no-go areas
    def is_intersection(self,coord1,coord2,coord3,coord4):
        #print "in intersection\n"
        x1 = coord1[0]
        y1 = coord1[1]
        x2 = coord2[0]
        y2 = coord2[1]
        x3 = coord3[0]
        y3 = coord3[1]
        x4 = coord4[0]
        y4 = coord4[1]

	if((x2-x1 == 0)):
		x2 += 0.000001
	if(x4-x3 == 0):
		x4 += 0.000001
	if(y2-y1 != 0):
		y2 += 0.000001
	if(y4-y3 != 0):
		y4 += 0.000001

        if((x2-x1 != 0) or (x4-x3 != 0) or (y2-y1 != 0) or (y4-y3 != 0)):
		slope1 = (y2-y1)/(x2-x1)
		slope2 = (y4-y3)/(x4-x3)
		#print "slope"
	else:
		slope1 = 10001
		slope2 = 10000
        yinter1 = y1- slope1*x1
        yinter1b = y2- slope1*x2
        yinter2 = y3 - slope2*x3
        yinter2b = y4 - slope2*x4

        xval = (yinter2 - yinter1) / (slope1 - slope2)
        yval = slope2*xval + yinter2

        if (((coord1[0] <= xval <= coord2[0])) or ((coord2[0] <= xval <= coord1[0]))
             and ((coord3[0] <= xval <= coord4[0]) or (coord4[0] <= xval <= coord3[0]))):
        	print "INTERSECTION at ",xval,",",yval
        	#print coord1
        	#print coord2
        	print (coord1[1] <= yval <= coord2[1] or coord2[1] <= yval <= coord1[1])
        	#print (yval <= coord4[1])

    		return 1
        else:
                return 0
        #print slope1
        #print slope2

    def validate_path(self, w):
    	valid = True

        for bad_area_id in self.nogo_areas.keys():
           prevName=""
           bad_area = self.nogo_areas[bad_area_id]
           print "THIS IS THE BAD_AREA_ID"
           print bad_area_id
           print "THIS IS THE BAD_AREA"
           print bad_area
           for strName in self.marker.positions.keys():
               #print "in markers, prev=",prevName
               if(prevName!=""):
            	   foo = 0
            	   #MainWindow.draw_marker_line(self, strName, prevName)
        	   #self.drawing_area.repaint()
        	   for i in range(len(bad_area)):
        	        #print bad_area[i]
	   		if(i == len(bad_area)-1):
			   if(MapOver.is_intersection(self,self.marker.positions[prevName],self.marker.positions[strName],bad_area[i],bad_area[0])):
		              if(self.marker.positions[strName][4] != -1 and self.marker.positions[prevName][4] != -1):
				    a,b,c,d,e = self.marker.positions[strName]
				    d = -1
				    self.marker.positions[strName] = a,b,c,d,e
				    a,b,c,d,e = self.marker.positions[prevName]
				    d = -1
				    self.marker.positions[prevName] = a,b,c,d,e
				    valid = False
         		else:
			   if(MapOver.is_intersection(self,self.marker.positions[prevName],self.marker.positions[strName],bad_area[i],bad_area[i+1])):
			      if(self.marker.positions[strName][4] != -1 and self.marker.positions[prevName][4] != -1):
				    a,b,c,d,e = self.marker.positions[strName]
				    d = -1
				    self.marker.positions[strName] = a,b,c,d,e
				    a,b,c,d,e = self.marker.positions[prevName]
				    d = -1
				    self.marker.positions[prevName] = a,b,c,d,e
				    valid = False
               prevName = strName


	self.marker.write_markers()
	self.drawing_area.repaint()
        self.asltw = ASALTWindow(
	                        self.conf,
	                        self.marker,
	                        valid,
	                        self.drawing_area
	                    )



    ## Called when new coordinates are obtained from the GPS
    def gps_callback(self, coord, mode):
        zl = self.get_zoom()
        tile = mapUtils.coord_to_tile((coord[0], coord[1], zl))
        # The map should be centered around a new GPS location
        if mode == GPS_CENTER or self.reCenter_gps:
            self.reCenter_gps = False
            self.drawing_area.center = tile
        # The map should be moved only to keep GPS location on the screen
        elif mode == GPS_ON_SCREEN:
            rect = self.drawing_area.get_allocation()
            xy = mapUtils.tile_coord_to_screen(
                (tile[0][0], tile[0][1], zl), rect, self.drawing_area.center)
            if xy:
                for x,y in xy:
                    x = x + tile[1][0]
                    y = y + tile[1][1]
                    if not(0 < x < rect.width) or not(0 < y < rect.height):
                        self.drawing_area.center = tile
                    else:
                        if GPS_IMG_SIZE[0] > x:
                            self.drawing_area.da_jump(1, zl, True)
                        elif x > rect.width - GPS_IMG_SIZE[0]:
                            self.drawing_area.da_jump(3, zl, True)
                        elif GPS_IMG_SIZE[1] > y:
                            self.drawing_area.da_jump(2, zl, True)
                        elif y > rect.height - GPS_IMG_SIZE[1]:
                            self.drawing_area.da_jump(4, zl, True)
            else:
                self.drawing_area.center = tile
        self.drawing_area.repaint()

    ## Creates the box that packs the comboBox & buttons
    def __create_upper_box(self):
        hbox = gtk.HBox(False, 5)

        gtk.stock_add([(gtk.STOCK_PREFERENCES, "", 0, 0, "")])
        return hbox

    ## Creates the box with the CheckButtons
    def __create_check_buttons(self):
        hbox = gtk.HBox(False, 10)

        self.cb_offline = gtk.CheckButton("Offlin_e")
        self.cb_offline.set_active(True)
        self.cb_offline.connect('clicked',self.offline_clicked)
        hbox.pack_start(self.cb_offline)

        self.cb_forceupdate = gtk.CheckButton("_Force update")
        self.cb_forceupdate.set_active(False)
        hbox.pack_start(self.cb_forceupdate)

        # self.cb_dropmarker = gtk.CheckButton("_Drop Markers")
        # self.cb_dropmarker.set_active(False)
        # self.cb_dropmarker.connect('clicked',self.drop_marker_mode)
        # hbox.pack_start(self.cb_dropmarker)


        bbox = gtk.HButtonBox()
        if mapGPS.available:
            cmb_gps = gtk.combo_box_new_text()
            for w in GPS_NAMES:
                cmb_gps.append_text(w)
            cmb_gps.set_active(self.conf.gps_mode)
            cmb_gps.connect('changed',self.gps_changed)
            bbox.add(cmb_gps)


        bbox.set_layout(gtk.BUTTONBOX_SPREAD)
        gtk.stock_add([(gtk.STOCK_HARDDISK, "_Download", 0, 0, "")])
        button = gtk.Button(stock=gtk.STOCK_HARDDISK)
        button.connect('clicked', self.download_clicked)
        bbox.add(button)

        cmb_layer = gtk.combo_box_new_text()
        for w in LAYER_NAMES:
            cmb_layer.append_text(w)
        cmb_layer.set_active(1)
        cmb_layer.connect('changed',self.layer_changed)
        bbox.add(cmb_layer)

        hbox.pack_start(bbox)
        return hbox

    def __create_top_paned(self):
        frame = gtk.Frame("Map Overlay")
        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(5)
        vbox.pack_start(self.__create_upper_box())
        vbox.pack_start(self.__create_check_buttons())
        frame.add(vbox)
        return frame

    def __create_left_paned(self):
        scale = gtk.VScale()
        scale.set_range(MAP_MIN_ZOOM_LEVEL, MAP_MAX_ZOOM_LEVEL)
        # scale.set_inverted(True)
        scale.set_property("update-policy", gtk.UPDATE_DISCONTINUOUS)
        scale.set_size_request(30, -1)
        scale.set_increments(1,1)
        scale.set_digits(0)
        scale.set_value(15)
        scale.connect("change-value", self.scale_change_value)
        scale.show()
        self.scale = scale
        return scale

    def __create_right_paned(self):
        da = DrawingArea(self.scale)
        self.drawing_area = da
        da.connect("expose-event", self.expose_cb)

        da.add_events(gtk.gdk.SCROLL_MASK)
        da.connect("scroll-event", self.scroll_cb)

        da.add_events(gtk.gdk.BUTTON1_MOTION_MASK)
        da.connect('motion-notify-event', self.da_motion)

        menu = gtk_menu(DA_MENU, self.menu_item_response)
        da.connect_object("event", self.da_click_events, menu)

        return self.drawing_area

    def right_paned(self):

        #frame = gtk.Frame("")
        # for parent in range(4):
            # piter = self.treestore.append(None, ['parent %i' % parent])
            # for child in range(3):
                # self.treestore.append(piter, ['child %i of parent %i' %
                                              # (child, parent)])

        self.mytree = gtk.TreeView(self.liststore)
        #self.myTree.connect("key-press-event", self.key_press_tree, listStore)

        strCols = ['Marker', 'Latitude', 'Longitude', 'Depth','Temperature']
        for intPos in range(len(strCols)):
            # Create a CellRenderers to render the data
            cell = gtk.CellRendererText()
            # Create the TreeViewColumns to display the data
            tvcolumn = gtk.TreeViewColumn(strCols[intPos])
            self.mytree.append_column(tvcolumn)
            tvcolumn.pack_start(cell, True)
            tvcolumn.set_attributes(cell, text=intPos)
            tvcolumn.set_sort_column_id(intPos)
            tvcolumn.set_resizable(True)
            if intPos == 0:
                tvcolumn.set_expand(True)
            else:
                tvcolumn.set_min_width(75)

         # make myTree searchable by location
        self.mytree.set_search_column(0)
        self.liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)

		# self.mytree = gtk.TreeView(self.liststore)
        # self.tvcolumn = gtk.TreeViewColumn('Data Information')
        # self.mytree.append_column(self.tvcolumn)
        # self.cell = gtk.CellRendererText()
        # self.tvcolumn.add_attribute(self.cell, 'text', 0)
        # self.mytree.set_search_column(0)
        # self.tvcolumn.set_sort_column_id(0)
        # self.mytree.set_reorderable(True)
		
        bpaned = gtk.VPaned()
        #bpaned.set_border_length(200)
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.add(self.mytree)
        bpaned.pack1(scrolledwindow, True, True) 
        #frame.add(bpaned)		
        return bpaned

        ## Zoom to the given pointer
    def do_zoom(self, zoom, doForce=False, dPointer=False):
        if (MAP_MIN_ZOOM_LEVEL <= zoom <= MAP_MAX_ZOOM_LEVEL):
            self.drawing_area.do_scale(
                zoom, self.get_zoom(), doForce, dPointer
            )
            self.scale.set_value(zoom)

    def menu_tools(self, w, strName):
        for intPos in range(len(TOOLS_MENU)):
            if strName.startswith(TOOLS_MENU[intPos]):
                mapTools.main(self, intPos)
                return True

    ## All the actions for the menu items
    def menu_item_response(self, w, strName):
        if strName == DA_MENU[ZOOM_IN]:
            self.do_zoom(self.get_zoom() - 1, True, self.myPointer)
        elif strName == DA_MENU[ZOOM_OUT]:
            self.do_zoom(self.get_zoom() + 1, True, self.myPointer)
        elif strName == DA_MENU[CENTER_MAP]:
            self.do_zoom(self.get_zoom(), True, self.myPointer)
        elif strName == DA_MENU[RESET]:
            self.do_zoom(MAP_MAX_ZOOM_LEVEL)
        elif strName == DA_MENU[BATCH_DOWN]:
            self.download_clicked(w, self.myPointer)
        elif strName == DA_MENU[EXPORT_MAP]:
            self.do_export(self.myPointer)
        elif strName == DA_MENU[ADD_MARKER]:
            self.add_marker(self.myPointer)

    ## Add a marker
    def add_marker(self, pointer=None):
        tile = mapUtils.pointer_to_tile(
            self.drawing_area.get_allocation(),
            pointer, self.drawing_area.center, self.get_zoom()
        )
        coord = mapUtils.tile_to_coord(tile, self.get_zoom())
	markerdata = [coord, len(self.marker.positions)+1, 0]
	#coord.insert(0,idnum)
	#Append default wait time of zero
	#coord.append(0)
        self.marker.append_marker(markerdata)
        self.marker.refresh()
        self.drawing_area.repaint()

    ## Export tiles to one big map
    def do_export(self, pointer=None):
        if (pointer is None):
            tile = self.drawing_area.center[0]
        else:
            tile, offset = mapUtils.pointer_to_tile(
                self.drawing_area.get_allocation(),
                pointer, self.drawing_area.center, self.get_zoom()
            )
        self.ctx_map.do_export(
            (tile[0], tile[1], self.get_zoom()),
            self.layer, not self.cb_offline.get_active(),
            self.conf.map_service, self.conf.cloudMade_styleID,
            size=(1024, 1024)
        )


    ## Handles Right & Double clicks events in the drawing_area
    def da_click_events(self, w, event):
        # Right-Click event shows the popUp menu
        if (event.type == gtk.gdk.BUTTON_PRESS) and (event.button != 1):
            self.myPointer = (event.x, event.y)
            w.popup(None, None, None, event.button, event.time)
        # Double-Click event Zoom In
        elif (event.type == gtk.gdk._2BUTTON_PRESS):
            print event.x
            print event.y
            print "COORDINATES"
            self.do_zoom(self.get_zoom() - 1, True,
                        (event.x, event.y))

    ## Handles the mouse motion over the drawing_area
    def da_motion(self, w, event):
        self.drawing_area.da_move(event.x, event.y, self.get_zoom())


    def expose_cb(self, drawing_area, event):
        #print "expose_cb"
        online = not self.cb_offline.get_active()
        force_update = self.cb_forceupdate.get_active()
        rect = drawing_area.get_allocation()
        zl = self.get_zoom()
        self.downloader.query_region_around_point(
            self.drawing_area.center, (rect.width, rect.height), zl, self.layer,
            gui_callback(self.tile_received),
            online=online, force_update=force_update,
            mapServ=self.conf.map_service,
            styleID=self.conf.cloudMade_styleID
        )
        self.draw_overlay(drawing_area, rect)

    def scroll_cb(self, widget, event):
        xyPointer = self.drawing_area.get_pointer()
        if (event.direction == gtk.gdk.SCROLL_UP):
            self.do_zoom(self.get_zoom() - 1, dPointer=xyPointer)
        else:
            self.do_zoom(self.get_zoom() + 1, dPointer=xyPointer)

    def scale_change_value(self, range, scroll, value):
        self.do_zoom(value)

    ##called everytime you move the map, draws over the map

    def draw_overlay(self, drawing_area, rect):
        def draw_image(imgPos, img, width, height):
            mct = mapUtils.coord_to_tile((imgPos[0], imgPos[1], zl))
            xy = mapUtils.tile_coord_to_screen(
                (mct[0][0], mct[0][1], zl), rect, self.drawing_area.center)
            if xy:
                for x,y in xy:
                    drawing_area.window.draw_pixbuf(gc, img, 0, 0,
                        x + mct[1][0] - width/2,
                        y + mct[1][1] - height/2,
                        width, height
                    )

        gc = drawing_area.style.black_gc
        zl = self.get_zoom()

        # Draw cross in the center
        if self.conf.show_cross:
            drawing_area.window.draw_pixbuf(gc, self.crossPixbuf, 0, 0,
                rect.width/2 - 6, rect.height/2 - 6, 12, 12)

        # Draw the selected location
        pixDim = self.marker.get_pixDim(zl)
        #print "this is the GPS location"
        location = (self.lat[0] + "," +self.long[0])  #sets location of selected location
        #print location
        locations = self.ctx_map.get_locations()
        if (location in locations.keys()):
            coord = self.ctx_map.get_locations()[location]
            img = self.marker.get_marker_pixbuf(zl, marker_row)
            draw_image(coord, img, pixDim, pixDim)
			
			# Zooms in to first coordinate
            self.drawing_area.center = mapUtils.coord_to_tile(coord)
            self.set_scale.set_value(coord[2])
            self.do_zoom(7, True, (399, 310))
        else:
            coord = (None, None, None)
			
            # self.do_zoom(self.get_zoom() - 1, True,
                        # (event.x, event.y))

        for bad_area_id in self.nogo_areas.keys():
            prevName=""
            bad_area = self.nogo_areas[bad_area_id]
        for i in range(len(bad_area)):
	        if(i == len(bad_area)-1):
	      	#print "i=",i
	            self.drawing_area.draw_marker_line(bad_area[i], bad_area[0], zl, pixDim,"red",3)
	        else:
	   	        self.drawing_area.draw_marker_line(bad_area[i], bad_area[i+1], zl, pixDim,"red",3)


        # Draw the markers
        img = self.marker.get_marker_pixbuf(zl, 1)
        _prefix = abspath(join(dirname(__file__), "../../images"))
        prevmark = ""
        for str in self.marker.positions.keys():
            # print "str"
            # print str
            mpos = self.marker.positions[str]
            # print "MPOS"
            # print mpos[0],mpos[1], mpos[2], mpos[3], mpos[4]
            if(self.marker.positions[str][3] == -1):
                img = self.marker.get_marker_pixbuf2(zl)
            if zl <= mpos[2] and (mpos[0] != coord[0] and mpos[1] != coord[0]):
                draw_image(mpos, img, pixDim, pixDim)
			
				#draws the Green Line
            if (prevmark != "" and zl <= mpos[2] and (mpos[0] != coord[0] and mpos[1] != coord[0])):
            	self.drawing_area.draw_marker_line(self.marker.positions[str], self.marker.positions[prevmark], zl, pixDim,"green",2)
            	if(self.marker.positions[prevmark][3] == -1):
            	    img = self.marker.get_marker_pixbuf2(zl)
            	else:
            	    img = self.marker.get_marker_pixbuf(zl, 0)
            	draw_image(self.marker.positions[prevmark], img, pixDim, pixDim)
            prevmark = str
            img = self.marker.get_marker_pixbuf(zl, mpos[4]+1)

	prevmark = ""
	# Draw vehicle position markers
	if(self.asltw is not None):
	    updates = self.asltw.get_updates()
	    if(updates != []):
	       for loc in updates:
	          img = self.marker.get_marker_pixbuf3(zl)
		  if (loc[0] != coord[0] and loc[1] != coord[0]):
		     draw_image(loc, img, pixDim, pixDim)
		     if (prevmark != "" and (loc[0] != coord[0] and loc[1] != coord[0])):
		        self.drawing_area.draw_marker_line(loc, prevmark, zl, pixDim,"purple",2)
		        draw_image(prevmark, img, pixDim, pixDim)
                  prevmark = loc


        # Draw GPS position
        if mapGPS.available:
            location = self.gps.get_location()
            if location is not None and (zl <= self.conf.max_gps_zoom):
                img = self.gps.pixbuf
                draw_image(location, img, GPS_IMG_SIZE[0], GPS_IMG_SIZE[1])

    def tile_received(self, tile_coord, layer):
        if self.layer == layer and self.get_zoom() == tile_coord[2]:
            da = self.drawing_area
            rect = da.get_allocation()
            xy = mapUtils.tile_coord_to_screen(tile_coord, rect, self.drawing_area.center)
            if xy:
                gc = da.style.black_gc
                force_update = self.cb_forceupdate.get_active()
                img = self.ctx_map.load_pixbuf(tile_coord, layer, force_update)
                for x,y in xy:
                    da.window.draw_pixbuf(gc, img, 0, 0, x, y,
                                          TILES_WIDTH, TILES_HEIGHT)

                if not self.cb_offline.get_active():
                    self.draw_overlay(da, rect)

    ## Handles the pressing of F11 & F12
    def full_screen(self, keyval):
        # F11 = 65480
        if keyval == 65480:
            if self.get_decorated():
                self.unmaximize()
                self.set_keep_above(True)
                self.set_decorated(False)
                self.maximize()
            else:
                self.set_keep_above(False)
                self.set_decorated(True)
                self.unmaximize()
        # F12 = 65481
        elif keyval == 65481:
            if self.get_border_width() > 0:
                self.left_panel.hide()
                self.top_panel.hide()
                self.set_border_width(0)
            else:
                self.left_panel.show()
                self.top_panel.show()
                self.set_border_width(10)
        # ESC = 65307
        elif keyval == 65307:
            self.left_panel.show()
            self.top_panel.show()
            self.set_border_width(10)
            self.set_keep_above(False)
            self.set_decorated(True)
            self.unmaximize()

    ## Handles the keyboard navigation
    def navigation(self, keyval, zoom):
        # Left  = 65361  Up   = 65362
        # Right = 65363  Down = 65364
        if keyval in range(65361, 65365):
            self.drawing_area.da_jump(keyval - 65360, zoom)

        # Page Up = 65365  Page Down = 65366
        # Home    = 65360  End       = 65367
        elif keyval == 65365:
           self.drawing_area.da_jump(2, zoom, True)
        elif keyval == 65366:
            self.drawing_area.da_jump(4, zoom, True)
        elif keyval == 65360:
           self.drawing_area.da_jump(1, zoom, True)
        elif keyval == 65367:
            self.drawing_area.da_jump(3, zoom, True)

        # Minus = [45,65453]   Zoom Out
        # Plus  = [61,65451]   Zoom In
        elif keyval in [45,65453]:
            self.do_zoom(zoom+1, True)
        elif keyval in [61,65451]:
            self.do_zoom(zoom-1, True)

        # Space = 32   Refresh the GPS
        elif event.keyval == 32:
            self.reCenter_gps = True

    ## Handles the Key pressing
    def key_press_event(self, w, event):
        # F11 = 65480, F12 = 65481, ESC = 65307
        if event.keyval in [65480, 65481, 65307]:
            self.full_screen(event.keyval)
        # F9 = 65478
        elif event.keyval == 65478:
            self.validate_path(w)
        # F2 = 65471
        elif event.keyval == 65471:
            self.do_export()
        # F4 = 65473
        elif event.keyval == 65473:
            fileName = FileChooser('.', 'Select KML File to import')
            if fileName:
                kml_to_markers(fileName, self.marker)

        # All Navigation Keys when in FullScreen
        elif self.get_border_width() == 0:
            self.navigation(event.keyval, self.get_zoom())


    ## Final actions before main_quit
    def on_delete(self, *args):
        self.hide()
        if mapGPS.available:
            self.gps.stop_all()
        self.downloader.stop_all()
        self.ctx_map.finish()
        # If there was an update show it
        if self.update:
            self.update.finish()
        return False
		
    def setup_nogo(self):
        #This is the area surrounding the available field area
        default_nogo = []
        self.localPath = os.path.expanduser(self.conf.init_path or DEFAULT_PATH)
        print "THIS IS THE LOCAL  PATH IN  MAPOVER"
        print self.localPath
        self.nogoPath = os.path.join(self.localPath, 'nogo')
        print "THIS IS THE NOGO  PATH IN  MAPOVER"
        print self.nogoPath
        if (os.path.exists(self.nogoPath)):
	    return fileUtils.read_bad(self.nogoPath)
	    
	else:
            fileUtils.write_bad(self.nogoPath,default_nogo)
            return fileUtils.read_bad(self.nogoPath)

    # def show_tool(self, tooltip, x, y):

        # window = self.window
		
        # self.label.set_label(tooltip)
        # w, h = windwo.size_request()
        # window.move(*self.location(x,y,w,h))
        # window.show()
        # self.__shown = True
		
    def hide_tool(self):
	
        self.window.hide()
        self.shown = False

    def show(self, parent=None):

        self.conf = MapConf()
        self.crossPixbuf = mapPixbuf.cross()
        print "file name is"
        print self.conf.upload_file
        print "got it"
        self.localP = os.path.expanduser(self.conf.init_path or DEFAULT_PATH)

        self.liststore = gtk.ListStore(int, str, str, str, str)

		# set the tool tips for the markers
        self.tooltips = gtk.Tooltips()

        if self.conf.upload_file == 20:
            print "this is the upload file"
            print self.conf.upload_file
        else:
            ifile = open(self.conf.upload_file, "rb")
            reader = csv.reader(ifile)
        
				
            rownum = 0
            self.lat = {}
            self.long = {}
            self.h1 = {}
            self.h2 = {}
            self.h3 = {}
            self.h4 = {}
		
            for row  in reader:
    # Save header row.
                if rownum == 0:
                    self.temp_file = open(os.path.join(self.localP, 'nogo'), 'w')
                    new_file = open('C:/Documents and Settings/dascenci/Desktop/GMAP_REPO_MAIN/new_file.dat', 'w')
                    print (row)
                    self.lat[0] = row[0]
                    self.long[0] = row[1]
                    self.h1[0] = row[2]
                    self.h2[0] = row[3]
                    self.h3[0] = row[4]
                    self.h4[0] = row[5]
                    self.temp_file.write("")
                    #self.temp_file.write('1' + ',' + self.lat[0] + ',' +self.long[0] + '\n')
                    self.liststore.append([rownum+1, self.lat[0], self.long[0], self.h1[0],self.h2[0]]) 
                    new_file.write(self.lat[0] + '\t' + self.long[0] + '\t' + self.h1[0] + '\n')
                    print self.temp_file

#                print (lat[0] + " " + long[0] + " " +h1[0] + " " + h2[0] + " " +h3[0] + " " + h4[0])
                else:
                    self.temp_file = open(os.path.join(self.localP, 'nogo'), 'a')
                    new_file = open('C:/Documents and Settings/dascenci/Desktop/GMAP_REPO_MAIN/new_file.dat', 'a')
                    print ("DAT")
                    print new_file
                    print (row)
                    self.lat[rownum] = row[0]
                    self.long[rownum] = row[1]
                    self.h1[rownum] = row[2]
                    self.h2[rownum] = row[3]
                    self.h3[rownum] = row[4]
                    self.h4[rownum] = row[5]
                    self.temp_file.write("")
                    #self.temp_file.write('1' + ',' + self.lat[rownum] + ',' +self.long[rownum] + '\n')
                    new_file.write(self.lat[rownum] + '\t' +self.long[rownum] + '\t' + self.h1[rownum] + '\n')
                    self.liststore.append([rownum+1, self.lat[rownum], self.long[rownum], self.h1[rownum],self.h2[rownum]]) 
                    print self.temp_file
                #print (lat[rownum] + " " + long[rownum] + " " +h1[rownum] + " " + h2[rownum] + " " +h3[rownum] + " " + h4[rownum])
                    print rownum
                rownum += 1
                print rownum
            self.rows = rownum
            self.temp_file.close()
            ifile.close()


    	self.asltw = None
        self.nogo_areas = {}
        if mapGPS.available:
            self.gps = mapGPS.GPS(self.gps_callback,
                                  self.conf.gps_update_rate,
                                  self.conf.gps_mode)

        self.marker = MyMarkers(self.conf.init_path)
        self.ctx_map = MapServ(self.conf.init_path)
        self.downloader = MapDownloader(self.ctx_map)

        #Set layer to satellite
        self.layer = 1
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            print('hello')

        #self.connect('key-press-event', self.key_press_event)
        #self.connect('delete-event', self.on_delete)
        vpaned = gtk.VPaned()
        hpaned = gtk.HPaned()
        self.top_panel = self.__create_top_paned()
        self.left_panel = self.__create_left_paned()

        vpaned.pack1(self.top_panel, False, False)
        #hpaned.pack1(self.left_panel, False, False)
        hpaned.pack1(self.__create_right_paned(), True, True)
        hpaned.pack2(self.right_paned(), True, True)
        vpaned.add2(hpaned)
        self.nogo_areas = self.setup_nogo()
        print "THIS IS SELF.NOGO_AREAS"
        print self.nogo_areas
	
        #self.set_completion()
        #self.default_entry()
        locate_me = {}
		
        self.drawing_area.center = self.conf.init_center
		
        locate_me[0] = float(self.lat[0])
        locate_me[1] = float(self.long[0])
        locate_me[2] = 12
        tiles = mapUtils.coord_to_tile(locate_me)
        con_coord = mapUtils.tile_to_coord(tiles, 12)
        print con_coord[0], con_coord[1]
        self.do_zoom(7, True, (37, 271))
        

        #print self.drawing_area.center

        #self.entry.grab_focus()

        return vpaned


if __name__=="__main___":
    MapOver()
