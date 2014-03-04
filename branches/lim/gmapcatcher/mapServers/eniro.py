# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.eniro

from gmapcatcher.mapConst import *


max_zoom = 9
min_zoom = -1
skip_zooms = [8]
hybrid_background = [LAYER_SAT, LAYER_MAP]
layer_names = ['maps', 'aerial', 'topo', 'hybrid', 'chart']


## Returns a template URL for the Eniro
def layer_url_template(counter, layer, conf):
    if layer == LAYER_SAT:
        return 'http://ed-map-fi.wide.basefarm.net/ol_tiles/fi/%s/%i/%i/%i.jpeg'
    else:
        return 'http://ed-map-fi.wide.basefarm.net/ol_tiles/fi/%s/%i/%i/%i.png'


## Returns the URL to the Eniro tile
def get_url(counter, coord, layer, conf):
    template = layer_url_template(counter, layer, conf)
    if template:
        return template % (layer_names[layer], MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
