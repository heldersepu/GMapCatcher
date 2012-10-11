# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.trackWindow
# Widget that allows track control

import pygtk
pygtk.require('2.0')
import gtk

from customMsgBox import error_msg_non_blocking
from gmapcatcher.mapUtils import openGPX, saveGPX


class trackWindow(gtk.Window):
    def __init__(self, mapsObj):
        gtk.Window.__init__(self)
        self.mapsObj = mapsObj
        self.cb_tracks = list()
        vbox = gtk.VBox(False)
        vbox.pack_start(self._createTrackCB(mapsObj))
        vbox.pack_start(self._createButtons())

        self.cb_draw_distances = gtk.CheckButton('Draw distances')
        self.cb_draw_distances.connect('toggled', self.toggleDistance)
        vbox.pack_start(self.cb_draw_distances)

        self.set_title("GMapCatcher track control")
        self.set_border_width(10)
        self.add(vbox)
        self.connect('key-press-event', self.key_press)
        self.connect('delete-event', self.on_delete)
        self.show_all()
        self.update_widgets()

    def key_press(self, w, event):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [87, 119]:
            # W = 87,119
            self.on_delete()

    def on_delete(self, widget=None, event=None):
        self.mapsObj.trackw = None
        self.destroy()

    def _createTrackCB(self, mapsObj):
        frame = gtk.Frame()
        frame.set_border_width(10)
        vbox = gtk.VBox(False, 10)
        self.no_tracks = gtk.Label()
        self.no_tracks.set_text("<b><span foreground=\"red\">No Tracks Found!</span></b>")
        self.no_tracks.set_use_markup(True)
        vbox.pack_start(self.no_tracks)
        alignment = gtk.Alignment(0.5, 0.5, 0, 0)
        self.track_vbox = gtk.VBox(False)
        for i in range(len(mapsObj.tracks)):
            self.cb_tracks.append(gtk.CheckButton(mapsObj.tracks[i].name))
            self.cb_tracks[i].set_active(mapsObj.tracks[i] in mapsObj.shown_tracks)
            self.cb_tracks[i].connect('toggled', self.showTracks)
            self.track_vbox.pack_start(self.cb_tracks[i])
        alignment.add(self.track_vbox)
        vbox.pack_start(alignment)
        frame.add(vbox)
        return frame

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
        self.b_gps_export = gtk.Button('Export _GPS track')
        self.b_gps_export.connect('clicked', self.exportGPS)
        hbbox.pack_start(self.b_gps_export)
        return hbbox

    def update_widgets(self):
        for i in range(len(self.mapsObj.tracks)):
            # If track number is larger than length of current cb_tracks
            # it's new and checkbox needs to be added.
            if i + 1 > len(self.cb_tracks):
                self.cb_tracks.append(gtk.CheckButton(self.mapsObj.tracks[i].name))
                self.cb_tracks[-1].set_active(True)
                self.cb_tracks[-1].connect('toggled', self.showTracks)
                self.cb_tracks[-1].show()
                self.track_vbox.pack_start(self.cb_tracks[-1])
        hasTracks = len(self.cb_tracks) > 0
        self.no_tracks.set_visible(not hasTracks)
        self.b_export.set_sensitive(hasTracks)
        if self.mapsObj.gps and len(self.mapsObj.gps_track.points) > 1:
            self.b_gps_export.set_sensitive(True)
        else:
            self.b_gps_export.set_sensitive(False)

    def importTracks(self, w):
        tracks = openGPX()
        if tracks:
            self.mapsObj.tracks.extend(tracks)
            self.mapsObj.shown_tracks.extend(tracks)
            self.mapsObj.drawing_area.repaint()
        self.update_widgets()

    def exportTracks(self, w):
        tracksToExport = list()
        for i in range(len(self.mapsObj.tracks)):
            if self.cb_tracks[i].get_active():
                tracksToExport.append(self.mapsObj.tracks[i])
        if len(tracksToExport) > 0:
            saveGPX(tracksToExport)
        else:
            dialog = error_msg_non_blocking('No tracks', 'No tracks to export')
            dialog.connect('response', lambda dialog, response: dialog.destroy())
            dialog.show()

    def exportGPS(self, w):
        if self.mapsObj.gps and len(self.mapsObj.gps_track.points) > 1:
            saveGPX([self.mapsObj.gps_track])
        else:
            dialog = error_msg_non_blocking('No GPS points', 'No GPS points to save')
            dialog.connect('response', lambda dialog, response: dialog.destroy())
            dialog.show()

    def showTracks(self, w):
        tracksToShow = list()
        for i in range(len(self.mapsObj.tracks)):
            if self.cb_tracks[i].get_active():
                tracksToShow.append(self.mapsObj.tracks[i])
        self.mapsObj.shown_tracks = tracksToShow
        self.mapsObj.drawing_area.repaint()

    def toggleDistance(self, *args, **kwargs):
        self.mapsObj.draw_track_distance = self.cb_draw_distances.get_active()
        self.mapsObj.drawing_area.repaint()
