## @package gmapcatcher.mapServers.cloudMade
# All the interaction with CloudMade.com

import logging
log = logging.getLogger(__name__)

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL

API_KEY = "333d990d389d5e65a7714dd738b2fc77"

## Returns a template URL for CloudMade
def layer_url_template():
    return 'http://%s.tile.cloudmade.com/' + API_KEY +'/%i/%i/%i/%i/%i.png'

## Returns the URL to the CloudMade tile
def get_url(counter, coord, styleID=1, dimensions=256):
    server = ['a', 'b', 'c']
    return layer_url_template() % (server[counter % 3], styleID, dimensions,
                MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
