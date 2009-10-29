## @package src.openCycleMap
# All the interaction with OpenCycleMap.org

from mapConst import MAP_MAX_ZOOM_LEVEL

## Returns a template URL for the OpenCycleMap
def layer_url_template():
    
    return 'http://%s.andy.sandbox.cloudmade.com/tiles/cycle/%i/%i/%i.png'

## Returns the URL to the OpenCycleMap tile
def get_url(counter, coord):
    server = ['a', 'b', 'c']
    return layer_url_template() % (server[counter % 3], 
                MAP_MAX_ZOOM_LEVEL - coord[2], coord[0], coord[1])
