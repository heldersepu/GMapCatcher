## @package gmapcatcher.mapServers.stamenMaps
# All the interaction with Stamen.com
#
# Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under CC BY SA
#
# See http://maps.stamen.com/ for deatails.
#

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL


## Returns a template URL for the Stamen
def layer_url_template():
    return 'http://%stile.stamen.com/%s/%i/%i/%i.png'


## Returns the URL to the Stamen tile
def get_url(counter, layer_name, coord):
    server = ['', 'a.', 'b.', 'c.', 'd.']
    return layer_url_template() % (server[counter % 5], layer_name,
                MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
