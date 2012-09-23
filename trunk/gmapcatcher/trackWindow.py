# -*- coding: utf-8 -*-
## @package gmapcatcher.trackWindow
# Widget that allows track control

import pygtk
pygtk.require('2.0')
import gtk

from customMsgBox import error_msg_non_blocking
from customWidgets import *
from gtkThread import *
from mapUtils import saveGPX


class trackWindow(gtk.Window):
    def __init__(self, mapsObj, tracks, shown_tracks):
        gtk.Window.__init__(self)
        self.mapsObj = mapsObj
        self.tracks = tracks
        self.shown_tracks = shown_tracks
        self.cb_tracks = list()
        vbox = gtk.VBox(False)
        for i in range(len(tracks)):
            vbox.pack_start(self._createTrackCB(i, tracks[i]))
        vbox.pack_start(self._createButtons())
        self.set_title("GMapCatcher track control")
        self.set_border_width(10)
        self.add(vbox)
        self.show_all()

    def _createTrackCB(self, i, track):
        self.cb_tracks.append(gtk.CheckButton(track['name']))
        if track in self.shown_tracks:
            self.cb_tracks[i].set_active(True)
        return self.cb_tracks[i]

    def _createButtons(self):
        hbbox = gtk.HButtonBox()
        hbbox.set_border_width(10)
        hbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.b_export = gtk.Button('_Export selected tracks')
        self.b_export.connect('clicked', self.exportTracks)
        hbbox.pack_start(self.b_export)
        self.b_show = gtk.Button('_Show selected tracks')
        self.b_show.connect('clicked', self.showTracks)
        hbbox.pack_start(self.b_show)
        return hbbox

    def exportTracks(self, w):
        tracksToExport = list()
        for i in range(len(self.tracks)):
            if self.cb_tracks[i].get_active():
                tracksToExport.append(self.tracks[i])
        if len(tracksToExport) > 0:
            saveGPX(tracksToExport)
        else:
            dialog = error_msg_non_blocking('No tracks', 'No tracks to export')
            dialog.connect('response', lambda dialog, response: dialog.destroy())
            dialog.show()

    def showTracks(self, w):
        tracksToShow = list()
        for i in range(len(self.tracks)):
            if self.cb_tracks[i].get_active():
                tracksToShow.append(self.tracks[i])
        self.mapsObj.shown_tracks = tracksToShow
        self.mapsObj.drawing_area.repaint()
