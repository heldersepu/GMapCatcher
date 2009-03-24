#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import mapUtils
import googleMaps
import mapTools
from mapConst import *

class MainWindow(gtk.Window):

    center = ((0,0),(128,128))
    draging_start = (0, 0)
    current_zoom_level = MAP_MAX_ZOOM_LEVEL
    default_text = "Enter location here!"
    show_panels = True

    def error_msg(self, msg, buttons=gtk.BUTTONS_OK):
        dialog = gtk.MessageDialog(self,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_ERROR, buttons, msg)
        resp = dialog.run()
        dialog.destroy()
        return resp

    def do_scale(self, pos, pointer=None, force=False):
        pos = round(pos, 0)
        if (pos == round(self.scale.get_value(), 0)) and not force:
            return
        self.scale.set_value(pos)

        if (pointer == None):
            fix_tile, fix_offset = self.center
        else:
            rect = self.drawing_area.get_allocation()
            da_center = (rect.width / 2, rect.height / 2)

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
        self.drawing_area.queue_draw()

    def get_zoom_level(self):
        return int(self.scale.get_value())

    # Automatically display after selecting
    def on_completion_match(self, completion, model, iter):
        self.entry.set_text(model[iter][0])
        self.confirm_clicked(self)

    # Clean out the entry box if text = default
    def clean_entry(self, *args):
        if (self.entry.get_text() == self.default_text):
            self.entry.set_text("")
            self.entry.grab_focus()

    # Reset the default text if entry is empty
    def default_entry(self, *args):
        if (self.entry.get_text().strip() == ''):
            self.entry.set_text(self.default_text)

    # Handles the change event of the ComboBox
    def changed_combo(self, *args):
        str = self.entry.get_text()
        if (str.endswith(SEPARATOR)):
            self.entry.set_text(str.strip())
            self.confirm_clicked(self)

    # Show the combo list if is not empty
    def combo_popup(self):
        if self.combo.get_model().get_iter_root() != None:
            self.combo.popup()

    # Handles the pressing of arrow keys
    def key_press_combo(self, w, event):
        if event.keyval in [65362, 65364]:
            self.combo_popup()
            return True

    # Create a gtk Menu with the given items
    def gtk_menu(self, listItems):
        myMenu = gtk.Menu()
        for str in listItems:
            menu_items = gtk.MenuItem(str)
            myMenu.append(menu_items)
            menu_items.connect("activate", self.menu_item_response, str)
            menu_items.show()
        return myMenu

    # Handles the events in the Tools buttons
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
                mapUtils.force_repaint()

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

    def layer_changed(self, w):
        online = not self.cb_offline.get_active()
	self.layer = w.get_active()
        self.ctx_map.switch_layer(self.layer,online)
        self.drawing_area.queue_draw()

    # Creates a comboBox that will contain the locations
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

    # Creates the box that packs the comboBox & buttons
    def __create_upper_box(self):
        hbox = gtk.HBox(False, 5)

        gtk.stock_add([(gtk.STOCK_PREFERENCES, "", 0, 0, "")])
        button = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        menu = self.gtk_menu(TOOLS_MENU)
        button.connect_object("event", self.tools_button_event, menu)
        hbox.pack_start(button, False)

        self.combo = self.__create_combo_box()
        hbox.pack_start(self.combo)

        bbox = gtk.HButtonBox()
        button = gtk.Button(stock='gtk-ok')
        button.connect('clicked', self.confirm_clicked)
        bbox.add(button)
        hbox.pack_start(bbox, False, True, 15)
        return hbox

    # Creates the box with the CheckButtons
    def __create_check_buttons(self):
        hbox = gtk.HBox(False, 10)

        self.cb_offline = gtk.CheckButton("Offlin_e")
        self.cb_offline.set_active(True)
        hbox.pack_start(self.cb_offline)

        self.cb_forceupdate = gtk.CheckButton("_Force update")
        self.cb_forceupdate.set_active(False)
        hbox.pack_start(self.cb_forceupdate)

	self.cmb_layer = gtk.combo_box_new_text()
	for w in LAYER_NAMES:
	    self.cmb_layer.append_text(w)
	self.cmb_layer.set_active(0)
	self.cmb_layer.connect('changed',self.layer_changed)
        hbox.pack_start(self.cmb_layer)
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
        scale.set_value(MAP_MAX_ZOOM_LEVEL)
        scale.connect("change-value", self.scale_change_value)
        scale.show()
        self.scale = scale
        return scale

    def __create_right_paned(self):
        da = gtk.DrawingArea()
        self.drawing_area = da
        da.connect("expose_event", self.expose_cb)
        da.add_events(gtk.gdk.SCROLL_MASK)
        da.connect("scroll-event", self.scroll_cb)

        da.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        da.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        da.add_events(gtk.gdk.BUTTON1_MOTION_MASK)

        menu = self.gtk_menu(["Zoom In", "Zoom Out",
                              "Center map here", "Reset"])

        da.connect_object("event", self.da_click_events, menu)
        da.connect('button-press-event', self.da_button_press)
        da.connect('button-release-event', self.da_button_release)
        da.connect('motion-notify-event', self.da_motion)
        da.show()
        return self.drawing_area

    def do_zoom(self, value, doForce=False):
        if (MAP_MIN_ZOOM_LEVEL <= value <= MAP_MAX_ZOOM_LEVEL):
            self.do_scale(value, self.drawing_area.get_pointer(), doForce)

    def menu_tools(self, strName):
        for intPos in range(len(TOOLS_MENU)):
            if strName.startswith(TOOLS_MENU[intPos]):
                mapTools.main(self, self.ctx_map.configpath, intPos)
                return True

    # All the actions for the menu items
    def menu_item_response(self, w, strName):
        if strName.startswith("Zoom Out"):
            self.do_zoom(self.scale.get_value() + 1, True)
        elif strName.startswith("Zoom In"):
            self.do_zoom(self.scale.get_value() - 1, True)
        elif strName.startswith("Center map"):
            self.do_zoom(self.scale.get_value(), True)
        elif strName.startswith("Reset"):
            self.do_zoom(MAP_MAX_ZOOM_LEVEL)
        else:
            self.menu_tools(strName)

    # Change the mouse cursor over the drawing_area
    def da_set_cursor(self, dCursor = gtk.gdk.HAND1):
        cursor = gtk.gdk.Cursor(dCursor)
        self.drawing_area.window.set_cursor(cursor)

    # Handles Right & Double clicks events in the drawing_area
    def da_click_events(self, w, event):
        # Right-Click event shows the popUp menu
        if (event.type == gtk.gdk.BUTTON_PRESS) and (event.button != 1):
            w.popup(None, None, None, event.button, event.time)
        # Double-Click event Zoom In
        elif (event.type == gtk.gdk._2BUTTON_PRESS):
            self.do_zoom(self.scale.get_value() - 1, True)

    # Handles left (press click) event in the drawing_area
    def da_button_press(self, w, event):
        if (event.button == 1):
            self.draging_start = (event.x, event.y)
            self.da_set_cursor(gtk.gdk.FLEUR)

    # Handles left (release click) event in the drawing_area
    def da_button_release(self, w, event):
        if (event.button == 1):
            self.da_set_cursor()

    # Handles the mouse motion over the drawing_area
    def da_motion(self, w, event):
        x = event.x
        y = event.y
        if (x < 0) or (y < 0):
            return

        rect = self.drawing_area.get_allocation()
        if (x > rect.width) or (y > rect.height):
            return

        #print "mouse move: (%d, %d)" % (x, y)

        center_tile = self.center[0]
        self.center[1]

        center_offset = (self.center[1][0] + (self.draging_start[0] - x),
                         self.center[1][1] + (self.draging_start[1] - y))
        self.center = mapUtils.tile_adjustEx(self.get_zoom_level(),
                         center_tile, center_offset)
        self.draging_start = (x, y)
        self.drawing_area.queue_draw()
        # print "new draging_start: (%d, %d)" % self.draging_start
        # print "center: %d, %d, %d, %d" % (self.center[0][0],
        #         self.center[0][1],
        #         self.center[1][0],
        #         self.center[1][1])

    def expose_cb(self, drawing_area, event):
        online = not self.cb_offline.get_active()
        force_update = self.cb_forceupdate.get_active()
        rect = drawing_area.get_allocation()
        zl = self.get_zoom_level()
        mapUtils.do_expose_cb(self, zl, self.center, rect, online,
                              force_update, self.drawing_area.style.black_gc,
                              event.area)

    def scroll_cb(self, widget, event):
        if (event.direction == gtk.gdk.SCROLL_UP):
            self.do_zoom(self.scale.get_value() - 1)
        else:
            self.do_zoom(self.scale.get_value() + 1)

    def scale_change_value(self, range, scroll, value):
        if (MAP_MIN_ZOOM_LEVEL <= value <= MAP_MAX_ZOOM_LEVEL):
            self.do_scale(value)
        return

    # Handles the pressing of F11 & F12
    def full_screen(self, w, event):
        if event.keyval == 65480:
            if self.get_decorated():
                self.set_keep_above(True)
                self.set_decorated(False)
                self.maximize()
            else:
                self.set_keep_above(False)
                self.set_decorated(True)
                self.unmaximize()
        elif event.keyval == 65481:
            if self.show_panels:
                self.left_panel.hide()
                self.top_panel.hide()
            else:
                self.left_panel.show()
                self.top_panel.show()
            self.show_panels = not self.show_panels

    def __init__(self, parent=None):
        self.ctx_map = googleMaps.GoogleMaps()
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect("destroy", lambda *w: gtk.main_quit())

        self.connect('key-press-event', self.full_screen)
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
