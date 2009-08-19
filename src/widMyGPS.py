## @package src.widMyGPS
# Change Theme widget used to change the GTK theme.
# Displayed inside a tab in MapTools.

import gtk
import fileUtils
from mapConst import *
from customWidgets import _frame, lbl


class MyGPS():

    ## All the buttons at the bottom
    def __action_buttons(self, conf):
        def btn_revert_clicked(button, conf):
            self.load_combo(self.cmb_themes)
            self.cb_show_cross.set_active(conf.show_cross)
            intActive = 0
            for intPos in range(len(MAP_SERVERS)):
                if MAP_SERVERS[intPos] == conf.map_service:
                    intActive = intPos
            self.cmb_gps_mode.set_active(intActive)

        def btn_save_clicked(button, conf):
            conf.show_cross = int(self.cb_show_cross.get_active())
            conf.map_service = MAP_SERVERS[self.cmb_gps_mode.get_active()]
            conf.save()
            if self.cmb_themes.get_model():
                cmb_text = self.cmb_themes.get_active_text()
                if cmb_text:
                    fileUtils.write_gtkrc(cmb_text)

        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', btn_revert_clicked, conf)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', btn_save_clicked, conf)
        bbox.add(button)
        return bbox

    ## Option to display a cross in the center of the map
    def cross_check_box(self, show_cross):
        self.cb_show_cross = gtk.CheckButton('Show a "+" in the center of the map')
        self.cb_show_cross.set_active(show_cross)
        return _frame(" Mark center of the map ", self.cb_show_cross)

    ## ComboBox to change the GPS mode
    def gps_mode_combo(self, gps_mode):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Select your initial GPS mode: "))
        self.cmb_gps_mode = gtk.combo_box_new_text()
        for strMode in GPS_NAMES:
            self.cmb_gps_mode.append_text(strMode)
        self.cmb_gps_mode.set_active(gps_mode)
        hbox.pack_start(self.cmb_gps_mode)
        return _frame(" Map service ", hbox)

    ## Put all the GPS Widgets together
    def show(self, conf):
        def inner_box():
            vbox = gtk.VBox(False, 10)
            vbox.pack_start(self.cross_check_box(conf.show_cross))
            vbox.pack_start(self.gps_mode_combo(conf.gps_mode))
            hbox = gtk.HBox(False, 10)
            hbox.set_border_width(20)
            hbox.pack_start(vbox)
            return hbox

        vbox = gtk.VBox(False, 10)
        vbox.set_border_width(10)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Select new theme and restart GMapCatcher."))
        self.cmb_themes = gtk.combo_box_new_text()

        hbox.pack_start(self.cmb_themes)
        vbox.pack_start(_frame(" Available themes ", hbox), False)
        vbox.pack_start(inner_box(), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        buttons = self.__action_buttons(conf)
        hpaned.pack2(buttons, False, False)
        return hpaned

