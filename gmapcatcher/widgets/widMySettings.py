# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.widMySettings
# Settings widget that displays common settings.
# Displayed inside a tab in MapTools.

import os
import gtk
from gmapcatcher.mapConst import *
from customWidgets import SpinBtn, myFrame, lbl, FolderChooser


## This widget lets the user change common settings
class MySettings():
    ## Put all the settings Widgets together
    def show(self, parent):
        def _size(width, height):
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("Width:"), False)
            self.s_width = SpinBtn(width, 450, 1024, 100, 4)
            hbox.pack_start(self.s_width)

            hbox.pack_start(lbl("Height:"), False)
            self.s_height = SpinBtn(height, 400, 768, 100, 4)
            hbox.pack_start(self.s_height)
            return myFrame(" Size ", hbox)

        def _zoom(zoom):
            hbox = gtk.HBox(False, 10)
            self.s_zoom = SpinBtn(zoom)
            hbox.pack_start(self.s_zoom, False)
            return myFrame(" Zoom ", hbox)

        def _center(center):
            hbox = gtk.HBox(False, 0)
            hbox.pack_start(lbl(" (( "), False)
            self.s_center00 = SpinBtn(center[0][0], 0, 999999, 1, 6)
            hbox.pack_start(self.s_center00, False)
            hbox.pack_start(lbl(" ,  "), False)
            self.s_center01 = SpinBtn(center[0][1], 0, 999999, 1, 6)
            hbox.pack_start(self.s_center01, False)
            hbox.pack_start(lbl(" ), ( "), False)
            self.s_center10 = SpinBtn(center[1][0], 0, 256, 32, 3)
            hbox.pack_start(self.s_center10, False)
            hbox.pack_start(lbl(" ,  "), False)
            self.s_center11 = SpinBtn(center[1][1], 0, 256, 32, 3)
            hbox.pack_start(self.s_center11, False)
            hbox.pack_start(lbl(" )) "), False)
            return myFrame(" Center ", hbox)

        def _status_save(conf):
            def status_combo(active_type_id):
                hbox = gtk.HBox(False, 10)
                hbox.pack_start(lbl(" Select status bar type "))
                self.cmb_status_type = gtk.combo_box_new_text()
                for strType in STATUS_TYPE:
                    self.cmb_status_type.append_text(strType)
                self.cmb_status_type.set_active(active_type_id)
                hbox.pack_start(self.cmb_status_type)
                return hbox

            def save_checkbox(active_bool):
                self.save_at_close_button = \
                        gtk.CheckButton(" Save View Params ")
                self.save_at_close_button.set_active(active_bool)
                return self.save_at_close_button
            status = myFrame(" Location Status ",
                            status_combo(conf.statusbar_type))
            save = myFrame(" Close Settings ",
                          save_checkbox(conf.save_at_close))
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(save)
            hbox.pack_start(status)
            return hbox

        def custom_path(conf):
            def repository_type_combo(repos_type_id):
                self.cmb_repos_type = gtk.combo_box_new_text()
                for strMode in REPOS_TYPE:
                    self.cmb_repos_type.append_text(strMode)
                self.cmb_repos_type.set_active(repos_type_id)
                return self.cmb_repos_type

            def get_folder(button):
                folderName = FolderChooser()
                if folderName:
                    self.entry_custom_path.set_text(folderName)

            def set_folder(button):
                self.cmb_repos_type.set_active(REPOS_TYPE_FILES)
                self.entry_custom_path.set_text(DEFAULT_PATH)

            vbox = gtk.VBox(False, 5)
            vbox.set_border_width(5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl(" This is the directory with all the images. "))
            button = gtk.Button("Reset to default")
            button.connect('clicked', set_folder)
            hbox.pack_start(button)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            myEntry = gtk.Entry()
            if conf.init_path:
                myEntry.set_text(conf.init_path)
            else:
                myEntry.set_text("None")
            cmbbox = repository_type_combo(conf.repository_type)
            hbox.pack_start(cmbbox, False)
            hbox.pack_start(myEntry)
            self.entry_custom_path = myEntry
            button = gtk.Button(" ... ")
            button.connect('clicked', get_folder)
            hbox.pack_start(button, False)
            vbox.pack_start(hbox)
            return myFrame(" Custom Maps Directory ", vbox)

        def btn_save_clicked(button):
            conf.init_center = ((self.s_center00.get_value_as_int()),
                                (self.s_center01.get_value_as_int())), \
                                ((self.s_center10.get_value_as_int()),
                                (self.s_center11.get_value_as_int()))

            conf.init_zoom = self.s_zoom.get_value_as_int()
            conf.init_width = self.s_width.get_value_as_int()
            conf.init_height = self.s_height.get_value_as_int()
            conf.statusbar_type = self.cmb_status_type.get_active()
            conf.save_at_close = self.save_at_close_button.get_active()

            if(os.pathsep == ';'):
                # we have windows OS, filesystem is case insensitive
                newPath = (self.entry_custom_path.get_text().lower()).strip()
                oldPath = conf.init_path.lower().strip()
            else:
                newPath = (self.entry_custom_path.get_text()).strip()
                oldPath = conf.init_path.strip()

            if (newPath != "" and newPath.lower() != "none") or (self.cmb_repos_type.get_active() != conf.repository_type):
                #if strTemp != (conf.init_path.lower()).strip():
                if (newPath != oldPath) or (self.cmb_repos_type.get_active() != conf.repository_type):
                    conf.init_path = self.entry_custom_path.get_text()
                    conf.repository_type = self.cmb_repos_type.get_active()
                    parent.ctx_map.initLocations(conf)
                    parent.drawing_area.repaint()
            else:
                conf.init_path = None
                conf.repository_type = self.cmb_repos_type.get_active()
            conf.save()
            parent.refresh()

        def _action_buttons(conf, parent):
            def btn_revert_clicked(button):
                self.s_center00.set_value(conf.init_center[0][0])
                self.s_center01.set_value(conf.init_center[0][1])
                self.s_center10.set_value(conf.init_center[1][0])
                self.s_center11.set_value(conf.init_center[1][1])

                self.s_zoom.set_value(conf.init_zoom)
                self.s_width.set_value(conf.init_width)
                self.s_height.set_value(conf.init_height)

                if conf.init_path:
                    self.entry_custom_path.set_text(conf.init_path)
                else:
                    self.entry_custom_path.set_text("None")

            bbox = gtk.HButtonBox()
            bbox.set_layout(gtk.BUTTONBOX_END)
            bbox.set_border_width(10)
            bbox.set_spacing(60)

            button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
            button.connect('clicked', btn_revert_clicked)
            bbox.add(button)

            button = gtk.Button(stock=gtk.STOCK_SAVE)
            button.connect('clicked', btn_save_clicked)
            bbox.add(button)
            return bbox

        def btn_use_current(button, parent):
            self.s_center00.set_value(parent.drawing_area.center[0][0])
            self.s_center01.set_value(parent.drawing_area.center[0][1])
            self.s_center10.set_value(parent.drawing_area.center[1][0])
            self.s_center11.set_value(parent.drawing_area.center[1][1])
            self.s_zoom.set_value(parent.get_zoom())
            dsize = parent.window.get_size()
            self.s_width.set_value(dsize[0])
            self.s_height.set_value(dsize[1])

        def key_press(widget, event):
            if (event.state & gtk.gdk.CONTROL_MASK) != 0 and \
                    event.keyval in [83, 115]:
                # S = 83, 115
                btn_save_clicked(0)

        hpaned = gtk.VPaned()
        vbox = gtk.VBox()
        vbox.set_border_width(10)

        hbox = gtk.HBox(False, 10)
        conf = parent.conf
        hbox.pack_start(_size(conf.init_width, conf.init_height))
        hbox.pack_start(_zoom(conf.init_zoom), False)
        vbox.pack_start(hbox, False)

        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_center(conf.init_center))
        bbox = gtk.HButtonBox()
        button = gtk.Button("Use Current")
        button.connect('clicked', btn_use_current, parent)
        bbox.add(button)
        hbox.pack_start(bbox)
        vbox.pack_start(hbox, False)

        vbox1 = gtk.VBox(False, 10)
        vbox1.set_border_width(5)
        vbox1.pack_start(_status_save(conf))
        vbox1.pack_start(custom_path(conf))
        vbox.pack_start(vbox1, False)

        hpaned.pack1(vbox, True, True)
        hpaned.pack2(_action_buttons(conf, parent), False, False)
        hpaned.connect('key-press-event', key_press)
        return hpaned
