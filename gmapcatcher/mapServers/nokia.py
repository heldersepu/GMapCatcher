## @package gmapcatcher.mapServers.nokia
# All the interaction with http://maps.nokia.com

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL


## Returns a template URL for the Yahoo mas
def layer_url_template(layer):
    map_server_query = ["normal", "hybrid", "terrain"]
    return 'http://%i.base.maps.api.here.com/maptile/2.1/maptile/newest/' + \
        map_server_query[layer] + \
        '.day/%i/%i/%i/256/png8?app_id=bC4fb9WQfCCZfkxspD4z&app_code=K2Cpd_EKDzrZb1tz0zdpeQ&lg=eng'


## Returns the URL to the nokia map tile
def get_url(counter, coord, layer, conf):
    return layer_url_template(layer) % (counter + 1, MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
