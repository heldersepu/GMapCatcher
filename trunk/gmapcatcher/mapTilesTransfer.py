# -*- coding: utf-8 -*-
## @package gmapcatcher.mapTilesTranswer
# Transwer tiles from respo 1 to repos 2


import threading
import time
import gobject

import mapUtils
from tilesRepo.tilesRepo import TilesRepository


class InvalidInputParametersError(Exception):
    pass


class TilesTransfer(threading.Thread):

    def __init__(self, trepos_source, trepos_destination, center, zooms, region, layer, overwrite_destination):
        """copy tiles from repos trepos_source to trepos_destination

        trepos_source: source repository
        trepos_destination: destination repository
        center: (lat, lon)
        zooms: (zoom_min, zoom_max)
        region: (width, height) [km]
        layer: what layer to transfer
        """

        threading.Thread.__init__(self)
        self.stop_lock = threading.Lock()

        # when set to True, thread should stop immediately
        self.stop = False

        self.trepos_source = trepos_source
        self.trepos_destination = trepos_destination

        self.center_lat = center[0]
        self.center_lon = center[1]
        self.zoom_min = int(zooms[0])
        self.zoom_max = int(zooms[1])
        self.reg_width = region[0]
        self.reg_height = region[1]
        self.layer = layer
        self.overwrite_destination = overwrite_destination

        if (not isinstance(trepos_source, TilesRepository)):
            raise InvalidInputParametersError("trepos_source is not subclass of TilesRepository")
        if (not isinstance(trepos_destination, TilesRepository)):
            raise InvalidInputParametersError("trepos_destination is not subclass of TilesRepository")
        if self.zoom_max < self.zoom_min:
            raise InvalidInputParametersError("Zoom max (%d) is less than zoom min (%d)." % (self.zoom_max, self.zoom_min))

    def get_tiles_range_for_zoom(self, zoom):
        # get tiles - copied from mapDownloader
        dlon = mapUtils.km_to_lon(mapUtils.nice_round(self.reg_width), self.center_lat)
        dlat = mapUtils.km_to_lat(mapUtils.nice_round(self.reg_height))

        if dlat > 170:
            dlat = 170
        if dlon > 358:
            dlon = 358

        top_left = mapUtils.coord_to_tile(
            (self.center_lat + dlat / 2, self.center_lon - dlon / 2, zoom)
        )
        bottom_right = mapUtils.coord_to_tile(
            (self.center_lat - dlat / 2, self.center_lon + dlon / 2, zoom)
        )

        # top_left[0][0], bottom_right[0][0], top_left[0][1], bottom_right[0][1]
        # xmin, xmax, ymin, ymax

        world_tiles = mapUtils.tiles_on_level(zoom)
        if bottom_right[0][0] - top_left[0][0] >= world_tiles:
            top_left[0][0], bottom_right[0][0] = 0, world_tiles - 1
        if bottom_right[0][1] - top_left[0][1] >= world_tiles:
            top_left[0][1], bottom_right[0][1] = 0, world_tiles - 1

        # xmin, xmax, ymin, ymax
        return(top_left[0][0], bottom_right[0][0], top_left[0][1], bottom_right[0][1])

    def set_callback_update(self, callback):
        self.callback_update = callback

    def set_callback_finish(self, callback):
        self.callback_finish = callback

    def count_all_tiles(self):
        all_tiles = 0

        zoom = self.zoom_min
        while zoom <= self.zoom_max:
            tiles_range = self.get_tiles_range_for_zoom(zoom)
            all_tiles = all_tiles + (tiles_range[1] - tiles_range[0] + 1) * (tiles_range[3] - tiles_range[2] + 1)
            zoom = zoom + 1

        return all_tiles

    def run(self):
        """Do transfer tiles.

        if overwrite is true, overwrite existing tiles in destination repository
        """

        gobject.idle_add(self.callback_update, "Computing tiles...")
        num_all_tiles = self.count_all_tiles()

        update_time = time.time()

        zoom = self.zoom_max

        tiles_count = 0
        tiles_written_count = 0
        while zoom >= self.zoom_min:
            tiles_range = self.get_tiles_range_for_zoom(zoom)

            ty = tiles_range[2]
            while ty <= tiles_range[3]:
                tx = tiles_range[0]
                while tx <= tiles_range[1]:
                    if self.should_i_stop():
                        return

                    if self.trepos_source.is_tile_in_local_repos((tx, ty, zoom), self.layer):
                        do_it = True

                        if not self.overwrite_destination:
                            if self.trepos_destination.is_tile_in_local_repos((tx, ty, zoom), self.layer):
                                do_it = False

                        if do_it:
                            tile_data = self.trepos_source.get_plain_tile((tx, ty, zoom), self.layer)
                            self.trepos_destination.store_plain_tile((tx, ty, zoom), self.layer, tile_data)
                            tiles_written_count = tiles_written_count + 1

                    tx = tx + 1
                    tiles_count = tiles_count + 1

                    if time.time() - update_time > 1:
                        percent = int((tiles_count / (1.0 * num_all_tiles)) * 100)
                        text = "Processed %d%% (%d of %d tiles)" % (percent, tiles_count, num_all_tiles)
                        gobject.idle_add(self.callback_update, text, percent)
                        update_time = time.time()

                ty = ty + 1

            zoom = zoom - 1
        gobject.idle_add(self.callback_finish, "All %d tiles processed." % (num_all_tiles, ))

    def should_i_stop(self):
        self.stop_lock.acquire()
        ret = self.stop
        self.stop_lock.release()
        return ret

    def set_stop(self, value):
        self.stop_lock.acquire()
        self.stop = value
        self.stop_lock.release()
