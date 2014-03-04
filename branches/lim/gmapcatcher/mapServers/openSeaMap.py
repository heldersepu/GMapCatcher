# -*- encoding: utf-8 -*-
## @package gmapcatcher.mapServers.openSeaMap

from gmapcatcher.mapConst import *

hybrid_background = [None, LAYER_MAP]


## Returns a template URL for the OpenSeaMap
def layer_url_template(layer, API_KEY):
    if layer == LAYER_CHA:
        return 'http://tiles.openseamap.org/seamark/%i/%i/%i.png'
    else:
        return 'http://%s.tile.cloudmade.com/' + API_KEY + '/%i/%i/%i/%i/%i.png'


## Returns the URL to the OpenSeaMap tile
def get_url(counter, coord, layer, conf):
    server = ['a', 'b', 'c']
    if layer == LAYER_CHA:
        return layer_url_template(layer, conf.cloudMade_API) % (MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
    else:
        return layer_url_template(layer, conf.cloudMade_API) % (server[counter % 3],
                conf.cloudMade_styleID, 256,
                MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
