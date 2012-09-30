## @package gmapcatcher.mapServers.WorldLO
# All the interaction with skyvector.net/tiles/302


## Returns a template URL for the WorldLO
def layer_url_template():
    return 'http://t%i.skyvector.net/tiles/302/1210/%i/%i/%i.jpg'


## Returns the URL to the WorldLO tile
def get_url(counter, coord, layer, conf):
    return layer_url_template() % (counter % 2, (coord[2] - 6) * 2, coord[0], coord[1])
