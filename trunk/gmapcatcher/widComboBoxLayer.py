# -*- coding: utf-8 -*-
## @package gmapcatcher.widComboBoxLayer
# ComboBoxLayer widget used to collect data to search

import gtk
from mapConst import *
from gobject import TYPE_STRING


## This widget is where we the available Layers
class ComboBoxLayer(gtk.ComboBox):

    def __init__(self, conf, current_layer):
        super(ComboBoxLayer, self).__init__()
        self.conf = conf
        self.current_layer = current_layer
        self.populate()

    def populate(self):
        store = gtk.ListStore(TYPE_STRING)
        if self.conf.oneDirPerMap:
            for kv in MAP_SERVICES:
                w = kv["serviceName"] + " " + kv["layerName"]
                iter = store.append()
                store.set(iter, 0, w)
        else:
            for w in range(len(LAYER_NAMES)):
                for kv in MAP_SERVICES:
                    if kv['serviceName'] == self.conf.map_service and kv['ID'] == w:
                        iter = store.append()
                        store.set(iter, 0, LAYER_NAMES[w])
        if (not self.conf.oneDirPerMap):
            if self.current_layer in NON_ONEDIR_COMBO_INDICES[self.conf.map_service]:
                self.set_active(
                    NON_ONEDIR_COMBO_INDICES[self.conf.map_service]
                    .index(self.current_layer))
            else:
                self.set_active(0)
                self.layer_changed(self)
        else:
            self.set_active(self.current_layer)
        self.set_model(store)
        self.set_entry_text_column(0)

    def refresh(self):
        self.set_model(None)
        self.populate()
