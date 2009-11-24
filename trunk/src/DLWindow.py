## @package src.DLWindow
# Widget that allows Download of entire locations

import math
import pygtk
pygtk.require('2.0')
import gtk

from mapConst import *
from mapArgs import MapArgs
from mapDownloader import MapDownloader
from customWidgets import _SpinBtn, _myEntry, _frame, lbl

import mapUtils
import mapServices
from gtkThread import *
from os.path import join
from time import gmtime, strftime


class DLWindow(gtk.Window):
    def __init__(self, coord, kmx, kmy, layer, init_path, mapServ, styleID):

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
            self.e_kmx = _myEntry("%.6g" % kmx, 10)
            hbox.pack_start(self.e_kmx, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("height:"))
            self.e_kmy = _myEntry("%.6g" % kmy, 10)
            hbox.pack_start(self.e_kmy, False)
            vbox.pack_start(hbox)
            return _frame(" Area (km) ", vbox)

        def _buttons():
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)
            self.b_download = gtk.Button(stock=gtk.STOCK_HARDDISK)
            self.b_download.connect('clicked', self.run, init_path)
            hbbox.pack_start(self.b_download)

            self.b_cancel = gtk.Button(stock='gtk-cancel')
            self.b_cancel.connect('clicked', self.cancel)
            self.b_cancel.set_sensitive(False)
            hbbox.pack_start(self.b_cancel)
            return hbbox

        print "DLWindow(", coord, kmx, kmy, layer, ')'
        self.mapService = mapServ
        self.styleID = styleID
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
        vbox.pack_start(_buttons())

        self.pbar = gtk.ProgressBar()
        self.pbar.set_text(" ")
        vbox.pack_start(self.pbar)
        self.add(vbox)

        self.set_title("GMapCatcher download")
        self.set_border_width(10)

        self.complete=[]
        self.processing=False
        self.gmap=None
        self.downloader=None
        self.connect('delete-event', self.on_delete)
        self.show_all()

    ## Start the download
    def run(self, w, init_path):
        args = MapArgs()
        if self.processing: return
        try:
            args.lat = float(self.e_lat0.get_text())
            args.lng = float(self.e_lon0.get_text())
            kmx = float(self.e_kmx.get_text())
            kmy = float(self.e_kmy.get_text())
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

        # Conversion of Km to coord
        dlon = kmx*180/math.pi/(R_EARTH*math.cos(args.lat*math.pi/180))
        dlat = kmy*180/math.pi/R_EARTH

        # creating our own gmap
        self.gmap = mapServices.MapServ(init_path)
        self.complete = []
        self.downloader = MapDownloader(self.gmap)
        if args.min_zl > args.max_zl:
            args.min_zl,args.max_zl = args.max_zl,args.min_zl

        # Save the map info
        self.save_info(init_path, str(args))

        self.all_placed = False
        self.processing = True
        for zoom in xrange(args.max_zl, args.min_zl-1, -1):
            self.downloader.query_region_around_location(
                args.lat, args.lng, dlat, dlon,
                zoom, layer,
                gui_callback(self.tile_received),
                mapServ=self.mapService,
                styleID=self.styleID
            )
        if self.downloader.qsize()==0:
            self.download_complete()
        self.all_placed = True

    ## Save the data to a text file
    def save_info(self, strPath, strInfo):
        timeStamp = strftime(" %d_%b_%Y %H.%M.%S", gmtime())
        file = open(join(strPath, 'gmap'+ timeStamp +'.bat'), "w")
        file.write(strInfo)
        file.close()

    def tile_received(self, coord, layer):
        #print "tile_received(", coord, layer, self.processing, self.downloader!=None,")"
        self.complete.append((coord, layer))
        ncomplete = len(self.complete)
        nqueued = self.downloader.qsize() if self.downloader else 0
        if nqueued==0 and self.all_placed:
            self.download_complete()
            return
        self.update_pbar("x=%d y=%d zoom=%d" % coord, ncomplete, ncomplete+nqueued)

    def update_pbar(self, text, pos, maxpos):
        self.pbar.set_text(text)
        self.pbar.set_fraction(float(pos)/maxpos)

    def download_complete(self):
        if self.downloader: self.downloader.stop_all()
        self.downloader = None
        self.processing = False
        self.b_cancel.set_sensitive(False)
        self.b_download.set_sensitive(True)
        self.update_pbar("Complete",0,1);

    def cancel(self,w):
        if self.downloader: self.downloader.stop_all()
        self.downloader = None
        self.processing = False
        self.b_cancel.set_sensitive(False)
        self.b_download.set_sensitive(True)
        self.update_pbar("Canceled",0,1);

    def on_delete(self,*params):
        if self.downloader: self.downloader.stop_all()
        return False

