## @package src.yahoo
# All the interaction with yahoo.com

from mapConst import MAP_MAX_ZOOM_LEVEL

## Returns a template URL for the Yahoo mas
def layer_url_template():
    return 'http://maps.yimg.com/hw/tile?locale=en&imgtype=png&yimgv=1.2&v=4.1&x=%i&y=%i&z=%i'

## Returns the URL to the Yahoo mas tile
def get_url(counter, coord):
    #server = ['a', 'b', 'c']
    return layer_url_template() % (
            coord[0],
            (((1 << (MAP_MAX_ZOOM_LEVEL - coord[2])) >> 1) - 1 - coord[1]) ,
            coord[2] + 1
        )
