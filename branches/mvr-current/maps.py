## @package maps
# This is the Main Window

#!/usr/bin/env python
import mapMark
import mapConf
import mapUtils
import googleMaps
import mapTools
import mapGPS
import mapPixbuf
import mapDownloader

from gtkThread import *
from mapConst import *
from DLWindow import DLWindow
from customWidgets import myToolTip, gtk_menu

class MainWindow(gtk.Window):

    center = ((0,0),(128,128))
    draging_start = (0, 0)
    current_zoom_level = MAP_MAX_ZOOM_LEVEL
    default_text = "Enter location here!"

    def error_msg(self, msg, buttons=gtk.BUTTONS_OK):
        dialog = gtk.MessageDialog(self,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_ERROR, buttons, msg)
        resp = dialog.run()
        dialog.destroy()
        return resp

    def do_scale(self, pos, pointer=None, force=False):
        pos = int(round(pos, 0))
        if (pos == round(self.scale.get_value(), 0)) and not force:
            return
        self.scale.set_value(pos)

        if (pointer == None):
            fix_tile, fix_offset = self.center
        else:
            rect = self.drawing_area.get_allocation()
            da_center = (rect.width // 2, rect.height // 2)

            fix_tile = self.center[0]
            fix_offset = self.center[1][0] + (pointer[0] - da_center[0]), \
                         self.center[1][1] + (pointer[1] - da_center[1])

            fix_tile, fix_offset = \
                mapUtils.tile_adjustEx(self.current_zoom_level,
                                       fix_tile, fix_offset)

        scala = 2 ** (self.current_zoom_level - pos)
        x = int((fix_tile[0] * TILES_WIDTH  + fix_offset[0]) * scala)
        y = int((fix_tile[1] * TILES_HEIGHT + fix_offset[1]) * scala)
        if (pointer != None) and not force:
            x = x - (pointer[0] - da_center[0])
            y = y - (pointer[1] - da_center[1])

        self.center = (x / TILES_WIDTH, y / TILES_HEIGHT), \
                      (x % TILES_WIDTH, y % TILES_HEIGHT)

        self.current_zoom_level = pos
        self.repaint()

    def get_zoom_level(self):
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
        if self.combo.get_model().get_iter_root() != None:
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

    def set_completion(self):
        completion = gtk.EntryCompletion()
        completion.connect('match-selected', self.on_completion_match)
        self.entry.set_completion(completion)
        completion.set_model(self.ctx_map.completion_model())
        completion.set_text_column(0)
        self.completion = completion
        # Populate the dropdownlist
        self.combo.set_model(self.ctx_map.completion_model(SEPARATOR))

    def confirm_clicked(self, button):
        location = self.entry.get_text()
        if (0 == len(location)):
            self.error_msg("Need location")
            self.entry.grab_focus()
            return
        if (location == self.default_text):
            self.clean_entry(self)
        else:
            locations = self.ctx_map.get_locations()
            if (not location in locations.keys()):
                if self.cb_offline.get_active():
                    if self.error_msg("Offline mode, cannot do search!" + \
                                      "      Would you like to get online?",
                                      gtk.BUTTONS_YES_NO) != gtk.RESPONSE_YES:
                        self.combo_popup()
                        return
                self.cb_offline.set_active(False)

                location = self.ctx_map.search_location(location)
                if (location[:6] == "error="):
                    self.error_msg(location[6:])
                    self.entry.grab_focus()
                    return

                self.entry.set_text(location)
                self.set_completion()
                coord = self.ctx_map.get_locations()[location]
            else:
                coord = locations[location]
            print "%s at %f, %f" % (location, coord[0], coord[1])

            self.center = mapUtils.coord_to_tile(coord)
            self.current_zoom_level = coord[2]
            self.do_scale(coord[2], force=True)

    def offline_clicked(self, w):
        online = not self.cb_offline.get_active()
        if online:
             self.repaint()

    def gps_changed(self, w):
        self.gps.set_mode(w.get_active())

    def layer_changed(self, w):
        self.layer = w.get_active()
        self.repaint()

    def download_clicked(self,w):
        coord = mapUtils.tile_to_coord(self.center, self.current_zoom_level)
        rect = self.drawing_area.get_allocation()
        km_px = mapUtils.km_per_pixel(coord)
        dlw = DLWindow(coord, km_px*rect.width, km_px*rect.height,
                       self.layer, self.conf.init_path)
        dlw.show()

    ## Called when the map should be centered around a new GPS location
    def gps_center_callback(self, coord):
        self.center = mapUtils.coord_to_tile((coord[0], coord[1], self.current_zoom_level))
        self.repaint()

    ## Called when the GPS marker should be moved to a new location
    def gps_marker_callback(self):
        self.repaint()

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
        menu = gtk_menu(TOOLS_MENU, self.menu_item_response)
        button.connect_object("event", self.tools_button_event, menu)
        button.props.has_tooltip = True
        button.connect("query-tooltip", myToolTip, "Title", "Description here", "images/marker.png")
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
            self.cmb_gps = gtk.combo_box_new_text()
            for w in GPS_NAMES:
                self.cmb_gps.append_text(w)
            self.cmb_gps.set_active(0)
            self.cmb_gps.connect('changed',self.gps_changed)
            bbox.add(self.cmb_gps)

        bbox.set_layout(gtk.BUTTONBOX_SPREAD)
        gtk.stock_add([(gtk.STOCK_HARDDISK, "_Download", 0, 0, "")])
        button = gtk.Button(stock=gtk.STOCK_HARDDISK)
        button.connect('clicked', self.download_clicked)
        bbox.add(button)

        self.cmb_layer = gtk.combo_box_new_text()
        for w in LAYER_NAMES:
            self.cmb_layer.append_text(w)
        self.cmb_layer.set_active(0)
        self.cmb_layer.connect('changed',self.layer_changed)
        bbox.add(self.cmb_layer)

        hbox.pack_start(bbox)
        return hbox

    def __create_top_paned(self):
        frame = gtk.Frame("Query")
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
        scale.set_value(self.current_zoom_level)
        scale.connect("change-value", self.scale_change_value)
        scale.show()
        self.scale = scale
        return scale

    def __create_right_paned(self):
        da = gtk.DrawingArea()
        self.drawing_area = da
        da.connect("expose-event", self.expose_cb)
        da.add_events(gtk.gdk.SCROLL_MASK)
        da.connect("scroll-event", self.scroll_cb)

        da.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        da.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        da.add_events(gtk.gdk.BUTTON1_MOTION_MASK)

        menu = gtk_menu(["Zoom In", "Zoom Out", "Center map here",
                    "Reset", "", "Batch Download"], self.menu_item_response)

        da.connect_object("event", self.da_click_events, menu)
        da.connect('button-press-event', self.da_button_press)
        da.connect('button-release-event', self.da_button_release)
        da.connect('motion-notify-event', self.da_motion)
        da.show()
        return self.drawing_area

    def do_zoom(self, value, doForce=False, doGetPointer=True):
        if (MAP_MIN_ZOOM_LEVEL <= value <= MAP_MAX_ZOOM_LEVEL):
            if doGetPointer:
                self.do_scale(value, self.drawing_area.get_pointer(), doForce)
            else:
                self.do_scale(value, None, doForce)

    def menu_tools(self, strName):
        for intPos in range(len(TOOLS_MENU)):
            if strName.startswith(TOOLS_MENU[intPos]):
                mapTools.main(self, intPos)
                return True

    ## All the actions for the menu items
    def menu_item_response(self, w, strName):
        if strName.startswith("Zoom Out"):
            self.do_zoom(self.scale.get_value() + 1, True)
        elif strName.startswith("Zoom In"):
            self.do_zoom(self.scale.get_value() - 1, True)
        elif strName.startswith("Center map"):
            self.do_zoom(self.scale.get_value(), True)
        elif strName.startswith("Reset"):
            self.do_zoom(MAP_MAX_ZOOM_LEVEL)
        elif strName.startswith("Batch Download"):
            self.download_clicked(w)
        else:
            self.menu_tools(strName)

    ## Change the mouse cursor over the drawing_area
    def da_set_cursor(self, dCursor = gtk.gdk.HAND1):
        cursor = gtk.gdk.Cursor(dCursor)
        self.drawing_area.window.set_cursor(cursor)

    ## Handles Right & Double clicks events in the drawing_area
    def da_click_events(self, w, event):
        # Right-Click event shows the popUp menu
        if (event.type == gtk.gdk.BUTTON_PRESS) and (event.button != 1):
            w.popup(None, None, None, event.button, event.time)
        # Double-Click event Zoom In
        elif (event.type == gtk.gdk._2BUTTON_PRESS):
            self.do_zoom(self.scale.get_value() - 1, True)

    ## Handles left (press click) event in the drawing_area
    def da_button_press(self, w, event):
        if (event.button == 1):
            self.draging_start = (event.x, event.y)
            self.da_set_cursor(gtk.gdk.FLEUR)

    ## Handles left (release click) event in the drawing_area
    def da_button_release(self, w, event):
        if (event.button == 1):
            self.da_set_cursor()

    ## Handles the mouse motion over the drawing_area
    def da_motion(self, w, event):
        x = event.x
        y = event.y
        self.da_move(x, y)

    ## Move the drawing_area
    def da_move(self, x, y):
        rect = self.drawing_area.get_allocation()
        if (0 <= x <= rect.width) and (0 <= y <= rect.height):
            center_offset = (self.center[1][0] + (self.draging_start[0] - x),
                             self.center[1][1] + (self.draging_start[1] - y))
            self.center = mapUtils.tile_adjustEx(self.get_zoom_level(),
                             self.center[0], center_offset)
            self.draging_start = (x, y)
            self.repaint()

    ## Jumps in the drawing_area
    def da_jump(self, intDirection, doBigJump=False):
        # Left  = 1  Up   = 2
        # Right = 3  Down = 4
        intJump = 10
        if doBigJump:
            intJump = intJump * 10

        self.draging_start = (intJump * (intDirection == 3),
                              intJump * (intDirection == 4))
        self.da_move(intJump * (intDirection == 1),
                     intJump * (intDirection == 2))

    def expose_cb(self, drawing_area, event):
        #print "expose_cb"
        online = not self.cb_offline.get_active()
        force_update = self.cb_forceupdate.get_active()
        rect = drawing_area.get_allocation()
        zl = self.get_zoom_level()
        self.downloader.query_region_around_point(
            self.center, (rect.width, rect.height), zl, self.layer,
            gui_callback(self.tile_received),
            online=online, force_update=force_update)
        self.draw_overlay(drawing_area, rect)

    def repaint(self):
        self.drawing_area.queue_draw()

    def scroll_cb(self, widget, event):
        if (event.direction == gtk.gdk.SCROLL_UP):
            self.do_zoom(self.scale.get_value() - 1)
        else:
            self.do_zoom(self.scale.get_value() + 1)

    def scale_change_value(self, range, scroll, value):
        if (MAP_MIN_ZOOM_LEVEL <= value <= MAP_MAX_ZOOM_LEVEL):
            self.do_scale(value)
        return

    def draw_overlay(self, drawing_area, rect):
        gc = drawing_area.style.black_gc
        zl = self.current_zoom_level

        # Draw cross in the center
        if self.conf.show_cross:
            drawing_area.window.draw_pixbuf(gc, self.crossPixbuf, 0, 0,
                rect.width/2 - 6, rect.height/2 - 6, 12, 12)

        # Draw the markers
        img = self.marker.get_marker_pixbuf(zl)
        pixDim = self.marker.get_pixDim(zl)
        for str in self.marker.positions.keys():
            mpos = self.marker.positions[str]
            if zl <= mpos[2]:
                mct = mapUtils.coord_to_tile((mpos[0], mpos[1], zl))
                xy = mapUtils.tile_coord_to_screen(
                    (mct[0][0], mct[0][1], zl), rect, self.center)
                if xy:
                    for x,y in xy:
                        drawing_area.window.draw_pixbuf(gc, img, 0, 0,
                            x + mct[1][0] - pixDim/2,
                            y + mct[1][1] - pixDim/2,
                            pixDim, pixDim)

        # Draw GPS position
        if mapGPS.available:
            location = self.gps.get_location()
            if location is not None and (zl < 17):
                img = self.gps.pixbuf
                img_size = (48, 48)
                mct = mapUtils.coord_to_tile((location[0], location[1], zl))
                xy = mapUtils.tile_coord_to_screen(
                    (mct[0][0], mct[0][1], zl), rect, self.center)
                if xy:
                    for x,y in xy:
                        drawing_area.window.draw_pixbuf(gc, img, 0, 0, \
                            x + mct[1][0] - img_size[0] / 2,
                            y + mct[1][1] - img_size[1] / 2, \
                            img_size[0], img_size[1])

    def tile_received(self, tile_coord, layer):
        if self.layer == layer and self.current_zoom_level == tile_coord[2]:
            da = self.drawing_area
            rect = da.get_allocation()
            xy = mapUtils.tile_coord_to_screen(tile_coord, rect, self.center)
            if xy:
                gc = da.style.black_gc
                img = self.ctx_map.load_pixbuf(tile_coord, layer)
                for x,y in xy:
                    da.window.draw_pixbuf(gc, img, 0, 0, x, y,
                                          TILES_WIDTH, TILES_HEIGHT)

                self.draw_overlay(da, rect)

    ## Handles the pressing of F11 & F12
    def full_screen(self,keyval):
        # F11 = 65480
        if keyval == 65480:
            if self.get_decorated():
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

    ## Handles the keyboard navigation
    def navigation(self, keyval):
        # Left  = 65361  Up   = 65362
        # Right = 65363  Down = 65364
        if keyval in range(65361, 65365):
            self.da_jump(keyval - 65360)

        # Page Up = 65365  Page Down = 65366
        # Home    = 65360  End       = 65367
        elif keyval == 65365:
           self.da_jump(2, True)
        elif keyval == 65366:
            self.da_jump(4, True)
        elif keyval == 65360:
           self.da_jump(1, True)
        elif keyval == 65367:
            self.da_jump(3, True)

        # Minus = [45,65453]   Zoom Out
        # Plus  = [61,65451]   Zoom In
        elif keyval in [45,65453]:
           self.do_zoom(self.scale.get_value() + 1, True, False)
        elif keyval in [61,65451]:
            self.do_zoom(self.scale.get_value() - 1, True, False)

    ## Handles the Key pressing
    def key_press_event(self, w, event):
        # F11 = 65480, F12 = 65481
        if event.keyval in [65480, 65481]:
            self.full_screen(event.keyval)
        # All Navigation Keys when in FullScreen
        elif self.get_border_width() == 0:
            self.navigation(event.keyval)

    def on_delete(self,*args):
        if mapGPS.available:
            self.gps.stop_all()
        self.downloader.stop_all()
        self.ctx_map.finish()
        return False

    def __init__(self, parent=None):
        self.conf = mapConf.MapConf()
        self.center = self.conf.init_center
        self.current_zoom_level = self.conf.init_zoom
        self.crossPixbuf = mapPixbuf.cross()

        if mapGPS.available:
            self.gps = mapGPS.GPS(self.gps_center_callback,
                                  self.gps_marker_callback,
                                  self.conf.gps_update_rate)

        self.marker = mapMark.MyMarkers(self.conf.init_path)
        self.ctx_map = googleMaps.GoogleMaps(self.conf.init_path)
        self.downloader = mapDownloader.MapDownloader(self.ctx_map)
        self.layer=0
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect("destroy", lambda *w: gtk.main_quit())

        self.connect('key-press-event', self.key_press_event)
        self.connect('delete-event', self.on_delete)
        vpaned = gtk.VPaned()
        hpaned = gtk.HPaned()
        self.top_panel = self.__create_top_paned()
        self.left_panel = self.__create_left_paned()

        vpaned.pack1(self.top_panel, False, False)
        hpaned.pack1(self.left_panel, False, False)
        hpaned.pack2(self.__create_right_paned(), True, True)
        vpaned.add2(hpaned)

        self.add(vpaned)
        self.set_title(" GMapCatcher ")
        self.set_border_width(10)
        self.set_size_request(450, 400)
        self.set_default_size(self.conf.init_width, self.conf.init_height)
        self.set_completion()
        self.default_entry()
        self.show_all()

        self.da_set_cursor()
        self.entry.grab_focus()

def main():
    MainWindow()
    gtk.main()

if __name__ == "__main__":
    main()
