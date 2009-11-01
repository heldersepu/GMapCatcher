## @package src.mapServers.informationFreeway
# All the interaction with InformationFreeway.org

from src.mapConst import MAP_MAX_ZOOM_LEVEL

## Returns a template URL for the informationFreeway
def layer_url_template():
    return 'http://%s.tah.openstreetmap.org/Tiles/tile/%i/%i/%i.png'

## Returns the URL to the informationFreeway tile
def get_url(counter, coord):
    server = ['a', 'b', 'c']
    return layer_url_template() % (server[counter % 3], 
                MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
