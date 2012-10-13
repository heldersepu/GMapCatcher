# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.widStatusBar
# StatusBar widget used to display messages

import gtk


## This is the status bar widget 
class StatusBar(gtk.Statusbar):
    DEFAULT_TEXT = "GMapCatcher map viewer!"
    context_id = None

    def __init__(self):
        super(StatusBar, self).__init__()
        self.set_has_resize_grip(False)
        self.context_id = self.get_context_id("init")
        self.push(self.context_id, self.DEFAULT_TEXT)

    def clear(self):
        self.pop(self.context_id)
        
    def text(self, strText):
        self.clear()
        self.push(self.context_id, strText)

    def coordinates(self, lat, lon):
        self.text("Latitude: " + str(round(lat, 6)) + " Longitude: " + str(round(lon, 6)))

    def distance(self, z, dUnits, total_dist):
        self.text("Segment Distance = %.3f %s, Total distance = %.3f %s" % (z, dUnits, total_dist, dUnits))
