## @package gmapcatcher.mapServers.nokia
# All the interaction with http://maps.nokia.com

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL


## Returns a template URL for the Yahoo mas
def layer_url_template(layer):
    map_server_name = ["base", "aerial", "aerial"]
    map_server_query = ["normal", "hybrid", "terrain"]
    return 'http://%i.' + map_server_name[layer] + \
        '.maps.api.here.com/maptile/2.1/maptile/newest/' + \
        map_server_query[layer] + \
        '.day/%i/%i/%i/256/png8?app_id=VgTVFr1a0ft1qGcLCVJ6&' + \
        'app_code=LJXqQ8ErW71UsRUK3R33Ow&lg=eng'


## Returns the URL to the nokia map tile
def get_url(counter, coord, layer, conf):
    return layer_url_template(layer) % (counter + 1, MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
