## @package gmapcatcher.mapServers.yahoo
# All the interaction with yahoo.com

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL, LAYER_MAP, LAYER_SAT, LAYER_HYB


## Returns a template URL for the Yahoo mas
def layer_url_template(layer):
    if layer == LAYER_MAP:
        return 'http://maps.yimg.com/hw/tile?&v=9&imgtype=png&s=256&x=%i&y=%i&z=%i'
    elif layer == LAYER_SAT:
        return 'http://maps.yimg.com/ae/ximg?v=9&t=s&imgtype=png&s=256&x=%i&y=%i&z=%i'
    elif layer == LAYER_HYB:
        return 'http://maps.yimg.com/hx/tl?v=9&t=h&imgtype=png&s=256&x=%i&y=%i&z=%i'


## Returns the URL to the Yahoo map tile
def get_url(counter, coord, layer):
    #server = ['a', 'b', 'c']
    return layer_url_template(layer) % (
            coord[0],
            (((1 << (MAP_MAX_ZOOM_LEVEL - coord[2])) >> 1) - 1 - coord[1]),
            coord[2] + 1
        )
