# -*- coding: utf-8 -*-
## @package gmapcatcher.widComboBoxLayer
# ComboBoxLayer widget used to collect data to search

import gtk
from mapConst import *
from gobject import TYPE_STRING


## This widget is where we the available Layers
class ComboBoxLayer(gtk.ComboBoxEntry):

    def __init__(self, conf, current_layer):
        super(ComboBoxLayer, self).__init__()
        self.connect('key-press-event', self.key_press_combo)
        self.child.connect('key-press-event', self.key_press_combo)
        self.conf = conf
        self.populate()
        self.set_active(current_layer)

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

        self.set_model(store)
        self.set_text_column(0)
    
    ## Handles the pressing of keys    
    def key_press_combo(self, w, event):
        if event.keyval not in [65362, 65364]:
            self.combo_popup()
            return True

    ## Show the combo list if is not empty
    def combo_popup(self):
        if self.get_model().get_iter_root() is not None:
            self.popup()

    def refresh(self):
        self.child.set_text('')
        self.set_model(None)
        self.populate()
        self.combo_popup()
