# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.widMapExport
# MapExport widget used to display map export objects


import os
import gtk
import gmapcatcher.fileUtils as fileUtils
from gmapcatcher.widgets.customWidgets import myFrame, lbl, ProgressBar, SpinBtn
from gmapcatcher.mapConst import *


## This widget allows the user to modify the locations and markers
class MapExport(gtk.Frame):

    def __init__(self):
        super(MapExport, self).__init__()

        vboxCoord = gtk.VBox(False, 5)
        vboxCoord.set_border_width(10)

        self.entryUpperLeft = gtk.Entry()        
        self.entryLowerRight = gtk.Entry()

        hbox = gtk.HBox(False)
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(lbl("  Upper Left: "))
        vbox.pack_start(lbl(" Lower Right: "))
        hbox.pack_start(vbox, False, True)
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(self.entryUpperLeft)
        vbox.pack_start(self.entryLowerRight)
        hbox.pack_start(vbox)
        vboxCoord.pack_start(myFrame(" Corners' coordinates ", hbox))

        vboxInput = gtk.VBox(False, 5)
        vboxInput.set_border_width(10)
        vbox = gtk.VBox(False, 20)
        vbox.set_border_width(10)
        hboxSize = gtk.HBox(False, 20)
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(lbl("Width / Height:"), False, True)
        self.sbWidth = SpinBtn(TILES_WIDTH * 4, TILES_WIDTH, 99999, TILES_WIDTH, 5)
        hbox.pack_start(self.sbWidth, False, True)
        hbox.pack_start(lbl("/"), False, True)
        self.sbHeight = SpinBtn(TILES_HEIGHT * 3, TILES_HEIGHT, 99999, TILES_HEIGHT, 5)
        hbox.pack_start(self.sbHeight, False, True)
        hboxSize.pack_start(hbox)
        vbox.pack_start(hboxSize)

        hboxZoom = gtk.HBox(False, 5)
        hboxZoom.pack_start(lbl("    Zoom Level:"), False, True)
        self.expZoom = SpinBtn(6)
        hboxZoom.pack_start(self.expZoom, False, True)
        self.mode = gtk.combo_box_new_text()
        self.mode.append_text("L")
        self.mode.append_text("RGB")
        self.mode.append_text("RGBA")
        self.mode.append_text("RGBX")
        self.mode.append_text("CMYK")
        if os.name == "posix":
            self.mode.set_active(2)
        else:
            self.mode.set_active(1)
        hboxZoom.pack_start(lbl("    Mode:"), False, True)
        hboxZoom.pack_start(self.mode, False, True)
        vbox.pack_start(hboxZoom)        

        self.button = gtk.Button(stock='gtk-ok')        
        hboxInput = gtk.HBox(False, 5)
        hboxInput.pack_start(vbox)
        bbox = gtk.HButtonBox()
        bbox.add(self.button)
        hboxInput.pack_start(bbox)
        vboxInput.pack_start(myFrame(" Image settings ", hboxInput))

        self.export_box = gtk.HBox(False, 5)
        self.export_box.pack_start(vboxCoord)
        self.export_box.pack_start(vboxInput)
        self.export_pbar = ProgressBar(" Exporting... ")
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(self.export_box)
        hbox.pack_start(self.export_pbar)

        vFbox = gtk.VBox(False, 5)
        vFbox.set_border_width(5)
        vFbox.pack_start(hbox)        
        self.add(vFbox)
        self.set_label(" Export map to PNG image ")
