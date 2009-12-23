## @package src.mapServers.virtualEarth
# All the interaction with maps.live.com

#from src.mapConst import MAP_MAX_ZOOM_LEVEL

## Returns a template URL for the virtualEarth
def layer_url_template():
    return 'http://r%i.ortho.tiles.virtualearth.net/tiles/r%i.png?g=%i'

## Returns the URL to the virtualEarth tile
def get_url(counter, coord):
    version = 392
    print tile_to_quadkey(coord)
    return layer_url_template() % (counter, tile_to_quadkey(coord), version)

def tile_to_quadkey(coord):
    quadKey = []
    for num in xrange(coord[2], 0, -1):
        digit = 0
        mask = 1 << (num - 1)
        if (coord[0] and mask) != 0:  digit += 1
        if (coord[1] and mask) != 0:  digit += 2
        quadKey.append(`digit`)
    return ''.join(quadKey)
