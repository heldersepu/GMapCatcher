# -*- coding: utf-8 -*-
## @package gmapcatcher.gpsWindow
# Widget to show GPS information

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from gtkThread import *
import pango
from mapConst import MODE_NO_FIX


class gpsWindow(gtk.Window):
    def __init__(self, mapsObj):
        gtk.Window.__init__(self)
        self.mapsObj = mapsObj

        self.font = pango.FontDescription("24")
        self.speed_choices = ['kn', 'km/h', 'mph']
        self.gps_values = []

        vbox = gtk.VBox(False)
        vbox.pack_start(self._createLabels(mapsObj))
        self.add(vbox)
        self.set_title("GPS")
        self.set_border_width(10)
        self.update_widgets()
        self.show_all()

        gobject.timeout_add_seconds(1, self.update_widgets)

        # self.updateThread = Timer(1, self.update_widgets)
        # self.updateThread.start()

    def _createLabels(self, mapsObj):
        texts = ['GPS time', 'Latitude', 'Longitude', 'Speed', 'Heading', 'Altitude']
        table = gtk.Table(len(texts) + 2, 2)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        # table.set_homogeneous(True)
        self.fix_label = gtk.Label()
        self.fix_label.set_use_markup(True)
        self.fix_label.modify_font(self.font)
        table.attach(self.fix_label, 0, 2, 0, 1)
        for i in range(len(texts)):
            label = gtk.Label('<b>%s</b>' % texts[i])
            label.set_use_markup(True)
            label.set_alignment(0, 0.5)
            label.modify_font(self.font)
            table.attach(label, 0, 1, i + 1, i + 2)

            label = gtk.Label()
            label.set_alignment(0, 0.5)
            label.modify_font(self.font)
            self.gps_values.append(label)
            table.attach(self.gps_values[-1], 1, 2, i + 1, i + 2)
        self.cmb_speed = gtk.combo_box_new_text()
        for choices in self.speed_choices:
            self.cmb_speed.append_text('Speed unit: %s' % choices)
        self.cmb_speed.set_active(0)
        table.attach(self.cmb_speed, 0, 2, len(texts) + 1, len(texts) + 2)
        return table

    def update_widgets(self):
        if self.mapsObj.gps and self.mapsObj.gps.gpsfix:
            if self.mapsObj.gps.gpsfix.mode > MODE_NO_FIX:
                self.fix_label.set_text('<b><span foreground=\"green\">FIX</span></b>')
            else:
                self.fix_label.set_text('<b><span foreground=\"red\">NO FIX</span></b>')
            self.fix_label.set_use_markup(True)
            if self.mapsObj.gps.gpsfix.time != 0.0:
                gps_time = str(self.mapsObj.gps.gpsfix.time)
                self.gps_values[0].set_text('%s:%s:%s' % (gps_time[0:2], gps_time[2:4], gps_time[4:6]))
            else:
                self.gps_values[0].set_text('0.0')
            self.gps_values[1].set_text('%.4f' % self.mapsObj.gps.gpsfix.latitude)
            self.gps_values[2].set_text('%.4f' % self.mapsObj.gps.gpsfix.longitude)
            speed_unit = self.cmb_speed.get_active()
            if speed_unit == 1:
                speed = self.mapsObj.gps.gpsfix.speed * 1.852
            elif speed_unit == 2:
                speed = self.mapsObj.gps.gpsfix.speed * 1.150779
            else:
                speed = self.mapsObj.gps.gpsfix.speed
            self.gps_values[3].set_text('%.1f %s' % (speed, self.speed_choices[speed_unit]))
            self.gps_values[4].set_text('%.1f' % self.mapsObj.gps.gpsfix.track)
            self.gps_values[5].set_text('%.1f' % self.mapsObj.gps.gpsfix.altitude)
        return True



    # def _createTrackCB(self, mapsObj):
    #     frame = gtk.Frame()
    #     frame.set_border_width(10)
    #     vbox = gtk.VBox(False, 10)
    #     self.no_tracks = gtk.Label()
    #     self.no_tracks.set_text("<b><span foreground=\"red\">No Tracks Found!</span></b>")
    #     self.no_tracks.set_use_markup(True)
    #     vbox.pack_start(self.no_tracks)
    #     alignment = gtk.Alignment(0.5, 0.5, 0, 0)
    #     self.track_vbox = gtk.VBox(False)
    #     for i in range(len(mapsObj.tracks)):
    #         self.cb_tracks.append(gtk.CheckButton(mapsObj.tracks[i]['name']))
    #         self.cb_tracks[i].set_active(mapsObj.tracks[i] in mapsObj.shown_tracks)
    #         self.cb_tracks[i].connect('toggled', self.showTracks)
    #         self.track_vbox.pack_start(self.cb_tracks[i])
    #     alignment.add(self.track_vbox)
    #     vbox.pack_start(alignment)
    #     frame.add(vbox)
    #     return frame

    # def update_widgets(self):
    #     hasTracks = len(self.cb_tracks) > 0
    #     self.no_tracks.set_visible(not hasTracks)
    #     self.b_export.set_sensitive(hasTracks)
    #     self.b_gps_export.set_sensitive(self.mapsObj.gps and len(self.mapsObj.gps.gps_points) > 0)
