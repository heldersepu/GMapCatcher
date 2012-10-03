## @package gmapcatcher.mapServers.WorldVFR
# All the interaction with skyvector.net/tiles/301


max_zoom = 15
min_zoom = 7

## Returns a template URL for the WorldVFR
def layer_url_template():
    return 'http://t%i.skyvector.net/tiles/301/1210/%i/%i/%i.jpg'


## Returns the URL to the WorldVFR tile
def get_url(counter, coord, layer, conf):
    return layer_url_template() % (counter % 2, (coord[2] - 6) * 2, coord[0], coord[1])
