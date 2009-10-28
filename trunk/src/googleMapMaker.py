## @package src.googleMapMaker
# All the interaction with Google Map Maker

from mapConst import MAP_MAX_ZOOM_LEVEL

## Returns a template URL for the Google Map Maker
def layer_url_template():    
    return 'http://gt%d.google.com/mt/n=404&v=gwm.1168&x=%i&y=%i&zoom=%i'

## Returns the URL to the Google Map Maker tile
def get_url(counter, coord):
    return layer_url_template() % (counter, coord[0], coord[1], coord[2]+1)
