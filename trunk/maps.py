#!/usr/bin/env python

## @package maps
# This is the Main Window

import src.mapGPS as mapGPS
import src.mapUtils as mapUtils
import src.mapTools as mapTools
import src.mapPixbuf as mapPixbuf

from src.mapConst import *
from src.gtkThread import *
from src.mapConf import MapConf
from src.mapMark import MyMarkers
from src.DLWindow import DLWindow
from src.mapUpdate import CheckForUpdates
from src.mapServices import MapServ
from src.customMsgBox import error_msg
from src.mapDownloader import MapDownloader
from src.customWidgets import myToolTip, gtk_menu, FileChooser, lbl, _frame, _myEntry
from src.xmlUtils import kml_to_markers
from src.widDrawingArea import DrawingArea

class MainWindow(gtk.Window):

    default_text = "Enter location here!"
    gps = None
    update = None
    myPointer = None
    reCenter_gps = False
    showMarkers = True
    key_down = None

    ## Get the zoom level from the scale
    def get_zoom(self):
        return int(self.scale.get_value())

    ## Automatically display after selecting
    def on_completion_match(self, completion, model, iter):
        self.entry.set_text(model[iter][0])
        self.confirm_clicked(self)

    ## Clean out the entry box if text = default
    def clean_entry(self, *args):
        if (self.entry.get_text() == self.default_text):
            self.entry.set_text("")
            self.entry.grab_focus()

    ## Reset the default text if entry is empty
    def default_entry(self, *args):
        if (self.entry.get_text().strip() == ''):
            self.entry.set_text(self.default_text)

    ## Handles the change event of the ComboBox
    def changed_combo(self, *args):
        str = self.entry.get_text()
        if (str.endswith(SEPARATOR)):
            self.entry.set_text(str.strip())
            self.confirm_clicked(self)

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

    ## Set the auto-completion for the entry box
    def set_completion(self):
        completion = gtk.EntryCompletion()
        completion.connect('match-selected', self.on_completion_match)
        self.entry.set_completion(completion)
        completion.set_model(self.ctx_map.completion_model())
        completion.set_text_column(0)
        self.completion = completion
        # Populate the dropdownlist
        self.combo.set_model(self.ctx_map.completion_model(SEPARATOR))

    ## Search for the location in the Entry box
    def confirm_clicked(self, button):
        location = self.entry.get_text()
        if (0 == len(location)):
            error_msg(self, "Need location")
            self.entry.grab_focus()
            return
        if (location == self.default_text):
            self.clean_entry(self)
        else:
            locations = self.ctx_map.get_locations()
            if (not location in locations.keys()):
                if self.cb_offline.get_active():
                    if error_msg(self, "Offline mode, cannot do search!" + \
                                  "      Would you like to get online?",
                                  gtk.BUTTONS_YES_NO) != gtk.RESPONSE_YES:
                        self.combo_popup()
                        return
                self.cb_offline.set_active(False)

                location = self.ctx_map.search_location(location)
                if (location[:6] == "error="):
                    error_msg(self, location[6:])
                    self.entry.grab_focus()
                    return

                self.entry.set_text(location)
                self.set_completion()
                coord = self.ctx_map.get_locations()[location]
            else:
                coord = locations[location]
            print "%s at %f, %f" % (location, coord[0], coord[1])

            self.drawing_area.center = mapUtils.coord_to_tile(coord)
            self.scale.set_value(coord[2])
            self.do_zoom(coord[2], True)

    ## Handles the click in the offline check box
    def offline_clicked(self, w):
        self.drawing_area.repaint()
        if not self.cb_offline.get_active():
            self.do_check_for_updates()

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
        if self.conf.oneDirPerMap:
            self.conf.map_service = MAP_SERVICES[layer]["serviceName"]
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
                        self.layer, self.conf
                    )
        dlw.show()

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

    ## Creates a comboBox that will contain the locations
    def __create_combo_box(self):
        combo = gtk.combo_box_entry_new_text()
        combo.connect('changed', self.changed_combo)
        combo.connect('key-press-event', self.key_press_combo)

        entry = combo.child
        # Start search after hit 'ENTER'
        entry.connect('activate', self.confirm_clicked)
        # Launch clean_entry for all the signals/events below
        entry.connect("button-press-event", self.clean_entry)
        entry.connect("cut-clipboard", self.clean_entry)
        entry.connect("copy-clipboard", self.clean_entry)
        entry.connect("paste-clipboard", self.clean_entry)
        entry.connect("move-cursor", self.clean_entry)
        # Launch the default_entry on the focus out
        entry.connect("focus-out-event", self.default_entry)
        self.entry = entry
        return combo

    ## Creates the box that packs the comboBox & buttons
    def __create_upper_box(self):
        hbox = gtk.HBox(False, 5)

        gtk.stock_add([(gtk.STOCK_PREFERENCES, "", 0, 0, "")])
        button = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        button.set_size_request(34, -1)
        menu = gtk_menu(TOOLS_MENU, self.menu_tools)
        button.connect_object("event", self.tools_button_event, menu)
        button.props.has_tooltip = True
        button.connect("query-tooltip", myToolTip, "Tools",
                    "Set of tools to customise GMapCatcher", "marker.png")
        hbox.pack_start(button, False)

        self.combo = self.__create_combo_box()
        hbox.pack_start(self.combo)

        bbox = gtk.HButtonBox()
        button_go = gtk.Button(stock='gtk-ok')
        button_go.connect('clicked', self.confirm_clicked)
        bbox.add(button_go)

        hbox.pack_start(bbox, False, True, 15)
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

        bbox = gtk.HButtonBox()
        if mapGPS.available:
            cmb_gps = gtk.combo_box_new_text()
            for w in GPS_NAMES:
                cmb_gps.append_text(w)
            cmb_gps.set_active(self.conf.gps_mode)
            cmb_gps.connect('changed',self.gps_changed)
            bbox.pack_start(cmb_gps)

        gtk.stock_add([(gtk.STOCK_HARDDISK, "_Download", 0, 0, "")])
        button = gtk.Button(stock=gtk.STOCK_HARDDISK)
        button.connect('clicked', self.download_clicked)
        bbox.pack_start(button)

        cmb_layer = gtk.combo_box_new_text()
        if self.conf.oneDirPerMap:
            for kv in MAP_SERVICES:
                w = kv["serviceName"] + " " + kv["layerName"]
                cmb_layer.append_text(w)
        else:
            for w in LAYER_NAMES:
                cmb_layer.append_text(w)
        cmb_layer.set_active(LAYER_MAP)
        cmb_layer.connect('changed',self.layer_changed)
        self.cmb_layer = cmb_layer
        bbox.pack_start(cmb_layer)
        bbox.set_layout(gtk.BUTTONBOX_SPREAD)
        hbox.add(bbox)
        return hbox

    def __create_top_paned(self):
        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(5)
        vbox.pack_start(self.__create_upper_box())
        vbox.pack_start(self.__create_check_buttons())
        return _frame(" Query ", vbox, 0)

    def __create_bottom_paned(self):
        vboxCoord = gtk.VBox(False, 5)
        vboxCoord.set_border_width(5)

        entry1 = gtk.Entry()
        entry2 = gtk.Entry()
        entry3 = gtk.Entry()
        entry4 = gtk.Entry()

        hbox = gtk.HBox(False, 5)
        hbox.pack_start(lbl(" lat: "), False, True)
        hbox.pack_start(entry1)
        hbox.pack_start(lbl(" lon: "), False, True)
        hbox.pack_start(entry2)
        vboxCoord.pack_start(_frame(" Upper ", hbox))

        hbox = gtk.HBox(False, 5)
        hbox.pack_start(lbl(" lat: "), False, True)
        hbox.pack_start(entry3)
        hbox.pack_start(lbl(" lon: "), False, True)
        hbox.pack_start(entry4)
        vboxCoord.pack_start(_frame(" Lower ", hbox))

        vboxSize = gtk.VBox(False, 5)
        hbox = gtk.HBox(False, 5)
        vboxSize.pack_start(lbl(" Width: "), False, True)
        vboxSize.pack_start(_myEntry("1024"))
        vboxSize.pack_start(lbl(" Height: "), False, True)
        vboxSize.pack_start(_myEntry("1024"))

        button = gtk.Button(stock='gtk-ok')
        button.connect('clicked', self.do_export)
        bbox = gtk.HButtonBox()
        bbox.add(button)

        hbox = gtk.HBox(False, 5)
        hbox.pack_start(vboxCoord)
        hbox.pack_start(_frame(" Image Size ", vboxSize))
        hbox.pack_start(bbox)
        return _frame(" Export map to PNG image ", hbox)

    def __create_left_paned(self):
        scale = gtk.VScale()
        scale.set_range(MAP_MIN_ZOOM_LEVEL, MAP_MAX_ZOOM_LEVEL)
        # scale.set_inverted(True)
        scale.set_property("update-policy", gtk.UPDATE_DISCONTINUOUS)
        scale.set_size_request(30, -1)
        scale.set_increments(1,1)
        scale.set_digits(0)
        scale.set_value(self.conf.init_zoom)
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
            self.show_export(self.myPointer)
        elif strName == DA_MENU[ADD_MARKER]:
            self.add_marker(self.myPointer)

    ## Add a marker
    def add_marker(self, pointer=None):
        tile = mapUtils.pointer_to_tile(
            self.drawing_area.get_allocation(),
            pointer, self.drawing_area.center, self.get_zoom()
        )
        coord = mapUtils.tile_to_coord(tile, self.get_zoom())
        self.marker.append_marker(coord)
        self.refresh()

    ## Show the bottom panel with the export
    def show_export(self, pointer=None):
        self.maximize()
        self.left_panel.hide()
        self.top_panel.hide()
        self.bottom_panel.show()

    ## Export tiles to one big map
    def do_export(self, button, pointer=None):
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

        self.bottom_panel.hide()
        self.left_panel.show()
        self.top_panel.show()


    ## Handles Right & Double clicks events in the drawing_area
    def da_click_events(self, w, event):
        # Single click event
        if (event.type == gtk.gdk.BUTTON_PRESS):
            # Right-Click event shows the popUp menu
            if (event.button != 1):
                self.myPointer = (event.x, event.y)
                w.popup(None, None, None, event.button, event.time)
            # Ctrl + Click adds a marker
            elif (self.key_down == 65507):
                self.add_marker((event.x, event.y))
        # Double-Click event Zoom In or Out
        elif (event.type == gtk.gdk._2BUTTON_PRESS):
            # Alt + 2Click Zoom Out
            if (self.key_down == 65513):
                self.do_zoom(self.get_zoom() + 1, True, (event.x, event.y))
            # 2Click Zoom In
            else:
                self.do_zoom(self.get_zoom() - 1, True, (event.x, event.y))

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
            styleID=self.conf.cloudMade_styleID,
            language=self.conf.language
        )
        self.draw_overlay()

    def scroll_cb(self, widget, event):
        xyPointer = self.drawing_area.get_pointer()
        if (event.direction == gtk.gdk.SCROLL_UP):
            self.do_zoom(self.get_zoom() - 1, dPointer=xyPointer)
        else:
            self.do_zoom(self.get_zoom() + 1, dPointer=xyPointer)

    def scale_change_value(self, range, scroll, value):
        self.do_zoom(value)

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
                    self.draw_overlay()

    def draw_overlay(self):
        if self.bottom_panel.flags() & gtk.VISIBLE:
            self.drawing_area.draw_overlay(
                self.get_zoom(), self.conf, self.crossPixbuf,
            )
        else:
            self.drawing_area.draw_overlay(
                self.get_zoom(), self.conf, self.crossPixbuf,
                self.marker, self.ctx_map.get_locations(),
                self.entry.get_text(), self.showMarkers, self.gps
            )

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
                self.bottom_panel.hide()
                self.left_panel.show()
                self.top_panel.show()
                self.set_border_width(10)
        # ESC = 65307
        elif keyval == 65307:
            self.bottom_panel.hide()
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

        # Space = 32   ReCenter the GPS
        elif keyval == 32:
            self.reCenter_gps = True

        # M = 77,109  S = 83,115  T = 84,116
        elif not self.conf.oneDirPerMap:
            if keyval in [77, 109]:
                self.cmb_layer.set_active(LAYER_MAP)
            elif keyval in [83, 115]:
                self.cmb_layer.set_active(LAYER_SATELLITE)
            elif keyval in [84, 116]:
                self.cmb_layer.set_active(LAYER_TERRAIN)


    ## Handles the Key release
    def key_release_event(self, w, event):
        self.key_down = None

    ## Handles the Key pressing
    def key_press_event(self, w, event):
        self.key_down = event.keyval
        # F11 = 65480, F12 = 65481, ESC = 65307
        if event.keyval in [65480, 65481, 65307]:
            self.full_screen(event.keyval)
        # F1 = 65471  Help
        elif event.keyval == 65470:
            webbrowser_open(WEB_ADDRESS)
        # F2 = 65471
        elif event.keyval == 65471:
            self.show_export()
        # F4 = 65473
        elif event.keyval == 65473:
            fileName = FileChooser('.', 'Select KML File to import')
            if fileName:
                kmlResponse = kml_to_markers(fileName, self.marker)
                if kmlResponse:
                    error_msg(self, "There was an error importing: \n" + \
                        "\n" + str(type(kmlResponse)) + \
                        "\n" + str(kmlResponse)
                    )
        # F5 = 65474
        elif event.keyval == 65474:
            self.refresh()
        # F8 = 65477
        elif event.keyval == 65477:
            self.showMarkers = not self.showMarkers
            self.drawing_area.repaint()

        # All Navigation Keys when in FullScreen
        elif self.get_border_width() == 0:
            self.navigation(event.keyval, self.get_zoom())

    ## All the refresh operations
    def refresh(self):
        self.enable_gps()
        self.marker.refresh()
        self.drawing_area.repaint()

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

    def enable_gps(self):
        if mapGPS.available:
            self.gps = mapGPS.GPS(
                self.gps_callback,
                self.conf.gps_update_rate,
                self.conf.gps_mode
            )

    def __init__(self, parent=None):
        self.conf = MapConf()
        self.crossPixbuf = mapPixbuf.cross()
        self.marker = MyMarkers(self.conf.init_path)
        self.ctx_map = MapServ(self.conf.init_path, self.conf.repository_type)
        self.downloader = MapDownloader(self.ctx_map)
        self.layer = LAYER_MAP
        self.enable_gps()

        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect("destroy", lambda *w: gtk.main_quit())

        self.connect('key-press-event', self.key_press_event)
        self.connect('key-release-event', self.key_release_event)
        self.connect('delete-event', self.on_delete)

        self.top_panel = self.__create_top_paned()
        self.left_panel = self.__create_left_paned()
        self.bottom_panel = self.__create_bottom_paned()

        vpaned = gtk.VPaned()
        vpaned.pack1(self.top_panel, False, False)
        hpaned = gtk.HPaned()
        hpaned.pack1(self.left_panel, False, False)

        inner_vp = gtk.VPaned()
        inner_vp.pack1(self.__create_right_paned(), True, True)
        inner_vp.pack2(self.bottom_panel, False, False)

        hpaned.pack2(inner_vp, True, True)
        vpaned.add2(hpaned)
        self.add(vpaned)

        self.set_title(" GMapCatcher ")
        self.set_border_width(10)
        self.set_size_request(450, 400)
        self.set_default_size(self.conf.init_width, self.conf.init_height)
        self.set_completion()
        self.default_entry()
        self.drawing_area.center = self.conf.init_center
        self.show_all()

        self.bottom_panel.hide()
        self.drawing_area.da_set_cursor()
        self.entry.grab_focus()

def main():
    MainWindow()
    gtk.main()

if __name__ == "__main__":
    main()
