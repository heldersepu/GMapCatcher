# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.widComboBoxLayer
# ComboBoxLayer widget used to collect data to search

import gtk
from gmapcatcher.mapConst import *
from gobject import TYPE_STRING, TYPE_INT


## This widget is where we the available Layers
class ComboBoxLayer(gtk.ComboBoxEntry):

    def __init__(self, conf):
        super(ComboBoxLayer, self).__init__()
        self.connect('key-press-event', self.key_press_combo)
        self.child.connect('key-press-event', self.key_press_combo)
        self.conf = conf
        currentMap = self.populate()
        self.set_active(currentMap)

    def populate(self):
        store = ListStore()
        currentMap = 0
        bad_map_servers = self.conf.hide_map_servers.split(',')
        for mapSrv in MAP_SERVICES:
            mapName = MAP_SERVERS[mapSrv['ID']]
            if self.conf.oneDirPerMap:
                if not str(mapSrv['ID']) in bad_map_servers:
                    store.add(mapName, mapSrv['ID'], mapSrv['layers'][0])
                    if mapName == self.conf.map_service:
                        currentMap = len(store) - 1
                    if (len(mapSrv['layers']) > 0):
                        for ln in mapSrv['layers']:
                            if ln > 0:
                                w = mapName + " " + LAYER_NAMES[ln]
                                store.add(w, mapSrv['ID'], ln)
                                if mapName == self.conf.map_service and ln == self.conf.save_layer:
                                    currentMap = len(store) - 1
            else:
                if mapName == self.conf.map_service:
                    for ln in mapSrv['layers']:
                        store.add(LAYER_NAMES[ln], mapSrv['ID'], ln)
                        if ln == self.conf.save_layer:
                            currentMap = len(store) - 1
        self.set_model(store)
        self.set_text_column(0)
        return currentMap

    ## Handles the pressing of keys
    def key_press_combo(self, w, event):
        if event.keyval not in [65362, 65364, 65513]:
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


class ListStore(gtk.ListStore):
    def __init__(self):
        super(ListStore, self).__init__(TYPE_STRING, TYPE_INT, TYPE_INT)

    def add(self, str, int1, int2):
        iter = self.append()
        self.set(iter, 0, str)
        self.set(iter, 1, int1)
        self.set(iter, 2, int2)
