## @package gmapcatcher.mapServers.openTopoMap
# All the interaction with opentopomap.org

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL


## Returns a template URL for the opentopomap
def layer_url_template():
    return 'https://%s.tile.opentopomap.org/%i/%i/%i.png'


## Returns the URL to the opentopomap tile
def get_url(counter, coord, layer, conf):
    server = ['a', 'b', 'c']
    return layer_url_template() % (server[counter % 3],
                MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
