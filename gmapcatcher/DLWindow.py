# -*- coding: utf-8 -*-
## @package gmapcatcher.DLWindow
# Widget that allows Download of entire locations

import pygtk
pygtk.require('2.0')
import gtk

from mapArgs import MapArgs
from fileUtils import check_dir
from mapDownloader import MapDownloader
from customWidgets import _SpinBtn, _myEntry, _frame, lbl, FileChooser

import mapPixbuf
import mapUtils
import mapServices
from mapConst import *
from gtkThread import *
from os.path import join, isdir

class DLWindow(gtk.Window):

    def __init__(self, coord, kmx, kmy, layer, conf):

        def _zoom(zoom0, zoom1):
            out_hbox = gtk.HBox(False, 50)
            out_hbox.set_border_width(10)
            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("min:"), False)
            self.s_zoom0 = _SpinBtn(zoom0)
            self.s_zoom0.set_digits(0)
            in_hbox.pack_start(self.s_zoom0)
            out_hbox.pack_start(in_hbox)

            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("max:"), False)
            self.s_zoom1 = _SpinBtn(zoom1)
            self.s_zoom1.set_digits(0)
            in_hbox.pack_start(self.s_zoom1)
            out_hbox.pack_start(in_hbox)
            hbox = gtk.HBox()
            hbox.set_border_width(10)
            hbox.pack_start(_frame(" Zoom ", out_hbox, 0))
            return hbox

        def _center(lat0, lon0):
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("latitude:"))
            self.e_lat0 = _myEntry("%.6f" % lat0, 15, False)
            hbox.pack_start(self.e_lat0, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("longitude:"))
            self.e_lon0 = _myEntry("%.6f" % lon0, 15, False)
            hbox.pack_start(self.e_lon0, False)
            vbox.pack_start(hbox)
            return _frame(" Center ", vbox)

        def _area(kmx, kmy):
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("width:"))
            self.e_kmx = _myEntry("%.6g" % kmx, 10, False)
            hbox.pack_start(self.e_kmx, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("height:"))
            self.e_kmy = _myEntry("%.6g" % kmy, 10, False)
            hbox.pack_start(self.e_kmy, False)
            vbox.pack_start(hbox)
            return _frame(" Area (km) ", vbox)

        def _buttons(strFolder):
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)

            self.b_download = gtk.Button(stock=gtk.STOCK_HARDDISK)
            self.b_download.connect('clicked', self.run, conf.init_path, conf.repository_type, strFolder)
            hbbox.pack_start(self.b_download)

            hbox = gtk.HBox()
            gtk.stock_add([(gtk.STOCK_UNDELETE, "", 0, 0, "")])
            self.b_open = gtk.Button(stock=gtk.STOCK_UNDELETE)
            self.b_open.connect('clicked', self.do_open, strFolder)
            hbox.pack_start(self.b_open, padding=25)
            if isdir(fldDown):
                hbbox.pack_start(hbox)

            self.b_cancel = gtk.Button(stock='gtk-cancel')
            self.b_cancel.connect('clicked', self.cancel)
            self.b_cancel.set_sensitive(False)

            hbbox.pack_start(self.b_cancel)
            return hbbox

        fldDown = join(conf.init_path, 'download')
        print "DLWindow(", coord, kmx, kmy, layer, ')'
        self.conf = conf
        kmx = mapUtils.nice_round(kmx)
        kmy = mapUtils.nice_round(kmy)
        self.layer = layer
        gtk.Window.__init__(self)
        lat0 = coord[0]
        lon0 = coord[1]
        zoom0 = max(MAP_MIN_ZOOM_LEVEL, coord[2]-3)
        zoom1 = min(MAP_MAX_ZOOM_LEVEL, coord[2]+1)

        vbox = gtk.VBox(False)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_center(lat0, lon0))
        hbox.pack_start(_area(kmx, kmy))
        vbox.pack_start(hbox)
        vbox.pack_start(_zoom(zoom0, zoom1))
        vbox.pack_start(_buttons(fldDown))

        self.pbar = gtk.ProgressBar()
        self.pbar.set_text(" ")
        vbox.pack_start(self.pbar)
        self.add(vbox)

        self.set_title("GMapCatcher download")
        self.set_border_width(10)
        ico = mapPixbuf.ico()
        if ico:
            self.set_icon(ico)

        self.complete=[]
        self.processing=False
        self.gmap=None
        self.downloader=None
        self.connect('delete-event', self.on_delete)
        self.connect('key-press-event', self.key_press)
        self.show_all()

    ## Start the download
    def run(self, w, init_path, repostype, strFolder):
        # Creating our own gmap
        self.gmap = mapServices.MapServ(init_path, repostype)
        self.complete = []
        self.downloader = MapDownloader(self.gmap)
        if self.conf.map_service in NO_BULK_DOWN:
            dialog = gtk.MessageDialog(self,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL,(
                    ("This map service (%s) doesn't allow bulk downloading. "
                    "If you insist on doing so, you break its term of use. \n\n"
                    "Continue or cancel?") % (self.conf.map_service)))
            response = dialog.run()
            dialog.destroy()
            if response != gtk.RESPONSE_OK or STRICT_LEGAL:
                self.all_done("Canceled")
                return
        args = MapArgs()
        if self.processing: return
        try:
            args.lat = float(self.e_lat0.get_text())
            args.lng = float(self.e_lon0.get_text())
            args.width = float(self.e_kmx.get_text())
            args.height = float(self.e_kmy.get_text())
            args.min_zl = self.s_zoom0.get_value_as_int()
            args.max_zl = self.s_zoom1.get_value_as_int()
            layer = self.layer
        except ValueError:
            d = gtk.MessageDialog(self, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "Some field contain non-numbers")
            d.run()
            d.destroy()
            return
        self.b_cancel.set_sensitive(True)
        self.b_download.set_sensitive(False)
        self.b_open.set_sensitive(False)
        # Save the map info
        self.save_info(check_dir(strFolder), str(args))
        self.pbar.set_text(" ")
        self.processing = True
        self.downloader.bulk_download((args.lat, args.lng, 15),
                    (args.min_zl, args.max_zl), args.width, args.height,
                    layer, gui_callback(self.tile_received),
                    self.download_complete, False, self.conf)
        self.processing = False

    # Open a previously saved file and auto-populate the fields
    def do_open(self, w, strPath):
        fileName = FileChooser(strPath)
        if fileName:
            file = open(fileName, "r")
            for line in file:
                args = MapArgs(line.split(" "))

                self.e_lat0.set_text(str(args.lat))
                self.e_lon0.set_text(str(args.lng))

                self.e_kmx.set_text(str(args.width))
                self.e_kmy.set_text(str(args.height))

                self.s_zoom0.set_text(str(args.min_zl))
                self.s_zoom1.set_text(str(args.max_zl))
                return

    ## Save the data to a text file
    def save_info(self, strPath, strInfo):
        file = open(join(strPath, 'gmap'+ mapUtils.timeStamp() +'.bat'), "w")
        file.write(strInfo)
        file.close()

    def tile_received(self, coord, layer, download=False):
        self.complete.append((coord, layer))
        ncomplete = len(self.complete)
        nqueued = self.downloader.qsize() if self.downloader else 0
        if nqueued==0 and ((not self.downloader) or self.downloader.bulk_all_placed):
            self.download_complete()
            return
        self.update_pbar(
            "x=%d y=%d zoom=%d" % coord, ncomplete, ncomplete+nqueued
        )

    def update_pbar(self, text, pos, maxpos):
        percent = ""
        if pos != maxpos:
            percentfloat = float(pos)/maxpos
            self.pbar.set_fraction(percentfloat)
            if percentfloat > 0:
                percent = " [%.1f%%]" % (percentfloat * 100)
        self.pbar.set_text(text + percent)

    def download_complete(self):
        if self.pbar.get_text() != "Canceled":
            self.all_done("Complete")

    def cancel(self,w):
        self.all_done("Canceled")

    def all_done(self, strMessage):
        if self.downloader:
            self.downloader.stop_all()
        self.downloader = None
        self.processing = False
        self.b_cancel.set_sensitive(False)
        self.b_download.set_sensitive(True)
        self.b_open.set_sensitive(True)
        self.update_pbar(strMessage, 0, 1)

    def key_press(self, w, event):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [87, 119]:
            # W = 87,119
            self.on_delete()
            self.destroy()

    def on_delete(self,*params):
        if self.downloader:
            self.downloader.stop_all()
        return False

