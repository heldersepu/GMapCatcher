# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.seznamHist
# All the interaction with mapy.cz (mapy.seznam.cz)

from seznam import get_url_internal


def get_url(counter, coord, layer, conf):
    layer_names = ["army2", "army2", "relief-l", "hybrid"]
    return get_url_internal(counter, coord, layer_names[layer])


