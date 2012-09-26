# -*- coding: utf-8 -*-
## @package gmapcatcher.widChangeTheme
# Change Theme widget used to change the GTK theme.
# Displayed inside a tab in MapTools.

from mapConst import *
import gtk
import fileUtils
import mapHideMapServers
from customWidgets import myFrame, lbl


## This widget lets the user change the visual theme
class ChangeTheme():
    ## Load the items into the Combo box
    def load_combo(self, myCombo):
        listThemes = fileUtils.get_themes()
        actualTheme = fileUtils.read_gtkrc()
        intTheme = 0
        model = myCombo.get_model()
        model.clear()
        myCombo.set_model(None)
        for l in range(len(listThemes)):
            model.append([listThemes[l]])
            if listThemes[l] == actualTheme:
                intTheme = l
        myCombo.set_model(model)
        myCombo.set_active(intTheme)

    def btn_save_clicked(self, button, conf):
        conf.show_cross = int(self.cb_show_cross.get_active())
        memservice = conf.map_service
        memtype = conf.oneDirPerMap
        memscale = conf.scale_visible
        conf.oneDirPerMap = int(self.cb_oneDirPerMap.get_active())
        conf.map_service = self.cmb_service.get_active_text()
        conf.scale_visible = self.cb_view_scale.get_active()
        conf.save()
        if memservice != conf.map_service or memtype != conf.oneDirPerMap:
            self.mapswindow.cmb_layer.refresh()
        if conf.scale_visible != memscale:
            self.mapswindow.refresh()
        if self.cmb_themes.get_model():
            cmb_text = self.cmb_themes.get_active_text()
            if cmb_text:
                fileUtils.write_gtkrc(cmb_text)  # All the buttons at the bottom

    def __action_buttons(self, conf):
        def btn_revert_clicked(button, conf):
            self.load_combo(self.cmb_themes)
            self.cb_show_cross.set_active(conf.show_cross)
            intActive = 0
            for intPos in range(len(MAP_SERVERS)):
                if MAP_SERVERS[intPos] == conf.map_service:
                    intActive = intPos
            self.cmb_service.set_active(intActive)

        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', btn_revert_clicked, conf)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', self.btn_save_clicked, conf)
        bbox.add(button)
        return bbox

    ## Option to display a cross in the center of the map
    def cross_check_box(self, show_cross):
        self.cb_show_cross = gtk.CheckButton('Show a "+" in the center of the map')
        self.cb_show_cross.set_active(show_cross)
        return myFrame(" Mark center of the map ", self.cb_show_cross)

    def view_scale_check(self, view_scale):
        self.cb_view_scale = gtk.CheckButton('View scale of map')
        self.cb_view_scale.set_active(view_scale)
        return myFrame(' Map Scale ', self.cb_view_scale)

    def scale_cross_element(self, view_scale, show_cross):
        hbox = gtk.HBox()
        hbox.pack_start(self.cross_check_box(show_cross))
        hbox.pack_start(self.view_scale_check(view_scale))
        return hbox

    ## ComboBox to change the map service
    def service_combo(self, conf):
        vbox = gtk.VBox(False, 5)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Select your favorite map service: "))
        self.cmb_service = gtk.combo_box_new_text()
        intActive = 0
        bad_map_servers = conf.hide_map_servers.split(',')
        for intPos in range(len(MAP_SERVERS)):
            if not str(intPos) in bad_map_servers:
                self.cmb_service.append_text(MAP_SERVERS[intPos])
                if MAP_SERVERS[intPos] == conf.map_service:
                    intActive = len(self.cmb_service.get_model()) - 1
        self.cmb_service.set_active(intActive)
        hbox.pack_start(self.cmb_service)
        vbox.pack_start(hbox)

        # Check box for option to create a dir per Map service
        hbox = gtk.HBox()
        self.cb_oneDirPerMap = gtk.CheckButton("Use a different folder per Map Service")
        self.cb_oneDirPerMap.set_active(conf.oneDirPerMap)
        hbox.pack_start(self.cb_oneDirPerMap)

        event_box = gtk.EventBox()
        label = gtk.Label()
        label.set_text("<span foreground=\"blue\" underline=\"single\">Select Map Servers</span>")
        label.set_use_markup(True)
        event_box.add(label)
        event_box.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        event_box.connect("button_press_event", self.open_editor)
        hbox.pack_start(event_box)
        vbox.pack_start(hbox)
        return myFrame(" Map service ", vbox)

    def open_editor(self, *w):
        mapHideMapServers.main(self.mapswindow)

    def key_press(self, widget, event, conf):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [83, 115]:
            # S = 83, 115
            self.btn_save_clicked(0, conf)

    ## Put all the ChangeTheme Widgets together
    def show(self, conf):
        def inner_box():
            vbox = gtk.VBox(False, 10)
            vbox.pack_start(self.scale_cross_element(conf.scale_visible, conf.show_cross))
            vbox.pack_start(self.service_combo(conf))
            hbox = gtk.HBox(False, 10)
            hbox.set_border_width(20)
            hbox.pack_start(vbox)
            return hbox

        vbox = gtk.VBox(False, 10)
        vbox.set_border_width(10)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Select new theme and restart GMapCatcher."))
        self.cmb_themes = gtk.combo_box_new_text()

        self.load_combo(self.cmb_themes)
        hbox.pack_start(self.cmb_themes)
        vbox.pack_start(myFrame(" Available themes ", hbox), False)
        vbox.pack_start(inner_box(), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        buttons = self.__action_buttons(conf)
        hpaned.connect('key-press-event', self.key_press, conf)
        hpaned.pack2(buttons, False, False)
        return hpaned

    def __init__(self, mapswindow):
        self.mapswindow = mapswindow
