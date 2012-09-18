## @package gmapcatcher.mapServers.cloudMade
# All the interaction with CloudMade.com

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL


## Returns a template URL for CloudMade
def layer_url_template(API_KEY):
    return 'http://%s.tile.cloudmade.com/' + API_KEY + '/%i/%i/%i/%i/%i.png'


## Returns the URL to the CloudMade tile
def get_url(counter, coord, conf, dimensions=256):
    server = ['a', 'b', 'c']
    return layer_url_template(conf.cloudMade_API) % (server[counter % 3],
            conf.cloudMade_styleID, dimensions,
            MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
