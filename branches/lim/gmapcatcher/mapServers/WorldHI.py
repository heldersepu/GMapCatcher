## @package gmapcatcher.mapServers.WorldHI
# All the interaction with skyvector.net/tiles/304


max_zoom = 15
min_zoom = 8

## Returns a template URL for the WorldHI
def layer_url_template():
    return 'http://t%i.skyvector.net/tiles/304/1211/%i/%i/%i.jpg'


## Returns the URL to the WorldHI tile
def get_url(counter, coord, layer, conf):
    return layer_url_template() % (counter % 2, (coord[2] - 7) * 2, coord[0], coord[1])
