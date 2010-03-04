## @package src.mapServers.virtualEarth
# All the interaction with maps.live.com

#from src.mapConst import MAP_MAX_ZOOM_LEVEL

from src.mapConst import MAP_SERVICES

## Returns a template URL for the virtualEarth
def layer_url_template(layer):
    layers_name = {"vemap":"r", "vesat": "a", "veter":"h"}
    return 'http://' + layers_name[ MAP_SERVICES[layer]["TextID"] ] + \
           '%i.ortho.tiles.virtualearth.net/tiles/' + \
           layers_name[MAP_SERVICES[layer]["TextID"]] + '%s.png?g=%i'

## Returns the URL to the virtualEarth tile
def get_url(counter, coord, layer):
    version = 392
    return layer_url_template(layer) % (counter, tile_to_quadkey(coord), version)

def tile_to_quadkey(coord):
    quadKey = []
    for num in xrange(17 - coord[2], 0, -1):
        digit = 0
        mask = 1 << (num - 1)
        if (coord[0] & mask) != 0:  digit += 1
        if (coord[1] & mask) != 0:  digit += 2
        quadKey.append(`digit`)
    return ''.join(quadKey)
