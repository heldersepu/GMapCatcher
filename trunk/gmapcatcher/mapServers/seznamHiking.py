# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.seznamHiking
# All the interaction with mapy.cz (mapy.seznam.cz)

from seznam import get_url_internal


def get_url(counter, coord, layer, conf):
    layer_names = ["turist", "turist", "relief-l", "ttur"]
    return get_url_internal(counter, coord, layer_names[layer])
