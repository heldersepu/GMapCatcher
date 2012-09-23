# -*- coding: utf-8 -*-
## @package gmapcatcher.trackWindow
# Widget that allows track control

import pygtk
pygtk.require('2.0')
import gtk

from customMsgBox import error_msg_non_blocking
from customWidgets import *
from gtkThread import *
from mapUtils import openGPX, saveGPX


class trackWindow(gtk.Window):
    def __init__(self, mapsObj, tracks, shown_tracks):
        gtk.Window.__init__(self)
        self.mapsObj = mapsObj
        self.tracks = tracks
        self.shown_tracks = shown_tracks
        self.cb_tracks = list()
        self._createTrackCB()
        vbox = gtk.VBox(False)
        vbox.pack_start(self.track_vbox)
        vbox.pack_start(self._createButtons())
        self.set_title("GMapCatcher track control")
        self.set_border_width(10)
        self.add(vbox)
        self.show_all()

    def _createTrackCB(self):
        self.track_vbox = gtk.VBox(False)
        for i in range(len(self.tracks)):
            self.cb_tracks.append(gtk.CheckButton(self.tracks[i]['name']))
            self.cb_tracks[-1].connect('toggled', self.showTracks)
            if self.tracks[i] in self.shown_tracks:
                self.cb_tracks[-1].set_active(True)
            self.track_vbox.pack_start(self.cb_tracks[i])

    def _createButtons(self):
        hbbox = gtk.HButtonBox()
        hbbox.set_border_width(10)
        hbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.b_import = gtk.Button('_Import tracks')
        self.b_import.connect('clicked', self.importTracks)
        hbbox.pack_start(self.b_import)
        self.b_export = gtk.Button('_Export selected tracks')
        self.b_export.connect('clicked', self.exportTracks)
        hbbox.pack_start(self.b_export)
        return hbbox

    def importTracks(self, w):
        tracks = openGPX()
        if tracks:
            self.mapsObj.tracks.extend(tracks)
            self.mapsObj.shown_tracks.extend(tracks)
            self.mapsObj.drawing_area.repaint()
            for track in tracks:
                self.cb_tracks.append(gtk.CheckButton(track['name']))
                self.cb_tracks[-1].set_active(True)
                self.cb_tracks[-1].connect('toggled', self.showTracks)
                self.track_vbox.pack_start(self.cb_tracks[-1])
                self.cb_tracks[-1].show()

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
