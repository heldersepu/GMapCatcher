# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.googleMaps
# All the interaction with google.com

from gmapcatcher.mapConst import *

known_layers = {}


## Returns a template URL for the OpenSeaMap
def layer_url_template(counter, layer, conf):
    if layer == LAYER_HYB:
        return 'http://ed-map-fi.wide.basefarm.net/ol_tiles/fi/chart/%i/%i/%i.png'
    else:
        return 'http://ed-map-fi.wide.basefarm.net/ol_tiles/fi/maps/%i/%i/%i.png'


## Returns the URL to the OpenSeaMap tile
def get_url(counter, coord, layer, conf):
    template = layer_url_template(counter, layer, conf)
    if template:
        return template % (MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
