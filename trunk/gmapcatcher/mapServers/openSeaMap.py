# -*- encoding: utf-8 -*-
## @package gmapcatcher.mapServers.openSeaMap

from gmapcatcher.mapConst import *

hybrid_background = LAYER_MAP


## Returns a template URL for the OpenSeaMap
def layer_url_template(counter, layer, conf):
    if layer == LAYER_HYB:
        return 'http://tiles.openseamap.org/seamark/%i/%i/%i.png'
    else:
        server = ['a', 'b', 'c']
        return 'http://' + server[counter % 3] + '.tile.openstreetmap.org/%i/%i/%i.png'


## Returns the URL to the OpenSeaMap tile
def get_url(counter, coord, layer, conf):
    template = layer_url_template(counter, layer, conf)
    if template:
        return template % (MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
