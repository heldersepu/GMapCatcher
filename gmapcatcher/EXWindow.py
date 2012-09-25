# -*- coding: utf-8 -*-
## @package gmapcatcher.EXWindow
# Widget that allows Export of entire locations to new tiles repository

from mapConst import *
import pygtk
pygtk.require('2.0')
import gtk

from customWidgets import lbl, myEntry, myFrame, SpinBtn, FolderChooser

import tilesRepo.Factory as trFactory
import mapTilesTransfer

import mapPixbuf
import mapUtils
# from gtkThread import gui_callback


class EXWindow(gtk.Window):

    configpath = "None"
    repostype_id = REPOS_TYPE_FILES
    repository_temp_file = "repository_write_test.tmp"

    def __init__(self, mapServ, coord, kmx, kmy, layer, conf):

        def _zoom(zoom0, zoom1):
            out_hbox = gtk.HBox(False, 50)
            out_hbox.set_border_width(10)
            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("min:"), False)
            self.s_zoom0 = SpinBtn(zoom0)
            self.s_zoom0.set_digits(0)
            in_hbox.pack_start(self.s_zoom0)
            out_hbox.pack_start(in_hbox)

            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("max:"), False)
            self.s_zoom1 = SpinBtn(zoom1)
            self.s_zoom1.set_digits(0)
            in_hbox.pack_start(self.s_zoom1)
            out_hbox.pack_start(in_hbox)
            hbox = gtk.HBox()
            hbox.set_border_width(10)
            hbox.pack_start(myFrame(" Zoom ", out_hbox, 0))
            return hbox

        def _custom_path():
            def repository_type_combo(repos_type_id):
                self.cmb_repos_type = gtk.combo_box_new_text()
                for strMode in REPOS_TYPE:
                    self.cmb_repos_type.append_text(strMode)
                self.cmb_repos_type.set_active(repos_type_id)
                return self.cmb_repos_type

            def get_folder(button):
                #if os.path.isdir(self.entry_custom_path.get_text()):
                #    dir = self.entry_custom_path
                #else:
                #    dir = None
                folderName = FolderChooser()
                if folderName:
                    self.entry_custom_path.set_text(folderName)

            vbox = gtk.VBox(False, 5)
            vbox.set_border_width(5)
            hbox = gtk.HBox(False, 10)
            self.entry_custom_path = gtk.Entry()
            self.entry_custom_path.set_text(EXWindow.configpath)
            repository_type_combo(EXWindow.repostype_id)
            hbox.pack_start(self.cmb_repos_type, False)
            hbox.pack_start(self.entry_custom_path)
            button = gtk.Button(" ... ")
            button.connect('clicked', get_folder)
            hbox.pack_start(button, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            self.cb_overwrite_destination = gtk.CheckButton("Overwrite existing tiles in destination repository")
            hbox.pack_start(self.cb_overwrite_destination)
            vbox.pack_start(hbox)

            return myFrame(" Destination repository for export ", vbox)

        def _center(lat0, lon0):
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("latitude:"))
            self.e_lat0 = myEntry("%.6f" % lat0, 15, False)
            hbox.pack_start(self.e_lat0, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("longitude:"))
            self.e_lon0 = myEntry("%.6f" % lon0, 15, False)
            hbox.pack_start(self.e_lon0, False)
            vbox.pack_start(hbox)
            return myFrame(" Center ", vbox)

        def _area(kmx, kmy):
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("width:"))
            self.e_kmx = myEntry("%.6g" % kmx, 10, False)
            hbox.pack_start(self.e_kmx, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("height:"))
            self.e_kmy = myEntry("%.6g" % kmy, 10, False)
            hbox.pack_start(self.e_kmy, False)
            vbox.pack_start(hbox)
            return myFrame(" Area (km) ", vbox)

        def _buttons():
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)

            self.b_export = gtk.Button("Export")
            self.b_export.connect('clicked', self.on_b_export_clicked, self)
            hbbox.pack_start(self.b_export)

            self.b_stop = gtk.Button(stock='gtk-media-stop')
            self.b_stop.connect('clicked', self.on_b_stop_clicked)
            self.b_stop.set_sensitive(False)

            hbbox.pack_start(self.b_stop)
            return hbbox

        self.mapServ = mapServ
        self.conf = conf
        kmx = mapUtils.nice_round(kmx)
        kmy = mapUtils.nice_round(kmy)
        self.layer = layer
        gtk.Window.__init__(self)
        lat0 = coord[0]
        lon0 = coord[1]
        zoom0 = max(MAP_MIN_ZOOM_LEVEL, coord[2] - 3)
        zoom1 = min(MAP_MAX_ZOOM_LEVEL, coord[2] + 1)

        vbox = gtk.VBox(False)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_center(lat0, lon0))
        hbox.pack_start(_area(kmx, kmy))
        vbox.pack_start(hbox)
        vbox.pack_start(_zoom(zoom0, zoom1))
        vbox.pack_start(_custom_path())
        vbox.pack_start(_buttons())

        self.pbar = gtk.ProgressBar()
        self.pbar.set_text("...")
        vbox.pack_start(self.pbar)
        self.add(vbox)

        self.set_title("GMapCatcher export")
        self.set_border_width(10)
        ico = mapPixbuf.ico()
        if ico:
            self.set_icon(ico)

        self.complete = []
        self.processing = False
        self.gmap = None
        self.downloader = None
        self.connect('delete-event', self.on_delete)
        self.connect('key-press-event', self.key_press)
        self.show_all()

        self.transfer_thread = None

    # check some basic file operations
    def check_write_access_dir(self, directory):
        tmp_filename = os.path.join(directory, EXWindow.repository_temp_file)
        ret = True

        try:
            file = open(tmp_filename, 'w')
            file.write(EXWindow.repository_temp_file)
            file.close()
            os.unlink(tmp_filename)
        except:
            ret = False

        return ret

    ## Start the download
    def on_b_export_clicked(self, b_export, window):
        # Creating our own gmap
        drepos_path = window.entry_custom_path.get_text()
        # drepos_type = window.cmb_repos_type.get_active()

        if not self.check_write_access_dir(drepos_path):
            gmsg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Error while trying to modify to selected repository '" + drepos_path + "'")
            gmsg.run()
            gmsg.destroy()
            return

        self.b_stop.set_sensitive(True)
        self.b_export.set_sensitive(False)

        self.drepos = trFactory.get_tile_repository(self.mapServ, self.conf)

        lat = float(self.e_lat0.get_text())
        lng = float(self.e_lon0.get_text())
        width = float(self.e_kmx.get_text())
        height = float(self.e_kmy.get_text())
        min_zl = self.s_zoom0.get_value_as_int()
        max_zl = self.s_zoom1.get_value_as_int()

        self.transfer_thread = mapTilesTransfer.TilesTransfer(self.mapServ.tile_repository, self.drepos, (lat, lng), (min_zl, max_zl), (width, height), self.layer, self.cb_overwrite_destination.get_active())
        self.transfer_thread.set_callback_update(self.update_pbar)
        self.transfer_thread.set_callback_finish(self.finished)

        self.transfer_thread.start()

    def update_pbar(self, text, percent=None):
        self.pbar.set_text(text)
        if percent is not None:
            self.pbar.set_fraction(percent / 100.0)

    def finished(self, text):
        self.pbar.set_text(text)
        self.pbar.set_fraction(1)
        self.do_stop()

    def on_b_stop_clicked(self, w):
        self.do_stop()
        self.pbar.set_text("Export interrupted.")

    def do_stop(self):
        if self.transfer_thread is None:
            return

        if self.transfer_thread.isAlive():
            self.transfer_thread.set_stop(True)
            self.transfer_thread.join()

        self.transfer_thread = None

        self.drepos.finish()
        self.drepos = None

        self.b_stop.set_sensitive(False)
        self.b_export.set_sensitive(True)

    def key_press(self, w, event):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [87, 119]:
            # W = 87,119
            self.on_delete()
            self.destroy()

    def on_delete(self, *params):

        EXWindow.configpath = self.entry_custom_path.get_text()
        EXWindow.repostype_id = self.cmb_repos_type.get_active()

        self.do_stop()
        return False
