## @package gmapcatcher.mapServers.virtualEarth
# All the interaction with maps.live.com

#from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL


## Returns a template URL for the virtualEarth
def layer_url_template(layer):
    layers_name = ["r", "a", "h"]
    return 'http://' + layers_name[layer] + \
           '%i.ortho.tiles.virtualearth.net/tiles/' + \
           layers_name[layer] + '%s.png?g=%i'


## Returns the URL to the virtualEarth tile
def get_url(counter, coord, layer, conf):
    version = 392
    return layer_url_template(layer) % (counter, tile_to_quadkey(coord), version)


def tile_to_quadkey(coord):
    quadKey = []
    for num in xrange(17 - coord[2], 0, -1):
        digit = 0
        mask = 1 << (num - 1)
        if (coord[0] & mask) != 0:
            digit += 1
        if (coord[1] & mask) != 0:
            digit += 2
        quadKey.append(str(digit))  # Was there a reason for this to be "quadKey.append(`digit`)" ?
    return ''.join(quadKey)
