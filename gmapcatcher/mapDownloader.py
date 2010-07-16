# -*- coding: utf-8 -*-
## @package gmapcatcher.mapDownloader
# All downloading is done here

from __future__ import division
from mapConst import TILES_HEIGHT
from threading import Thread, Timer
from Queue import Queue
from traceback import print_exc

import fileUtils
import mapUtils
from mapConst import *
from math import floor,ceil


class DownloadTask:
    def __init__(self, coord, layer, callback=None,
                    force_update=False, conf=None):
        self.coord = coord
        self.layer = layer
        self.callback = callback
        self.force_update = force_update
        self.conf = conf

    def __str__(self):
        return "DownloadTask(%s,%s)" % (self.coord, self.layer)

## Downloads tiles from the web.
#
#    process_task gets tile using get_file() and processes post-processing via
#    callback. Callback function is (usually) tile_received() implemented in
#    DLWindow.py and maps.py. The only place where DownloaderThread is used is
#    from class MapDownloader.
class DownloaderThread(Thread):

    def __init__(self, ctx_map, inq, parent):
        Thread.__init__(self)
        self.ctx_map = ctx_map
        self.inq = inq
        self.parent = parent

    def run(self):
        while True:
            task = self.inq.get()
            #print "task=",task
            if (task is None):
                return
            try:
                self.process_task(task)
            except:
                print_exc() # but don't die
            self.inq.task_done()

    def process_task(self, task):
        # poznamka: filename tady neni potreba, nejaky sideeffect?
        #filename = self.ctx_map.get_file(
        #    task.coord, task.layer, True,
        #   task.force_update, task.mapServ, task.styleID
        #)
        self.ctx_map.get_tile(
            task.coord, task.layer, True,
            task.force_update, task.conf
        )
        if task.callback:
            #print "process_task callback", task
            task.callback(False, task.coord, task.layer, True)
        self.parent.queued.remove((task.coord, task.layer))

## Main class used for downloading tiles.
#
#  Class is used from:
#      - download.py
#      - DLWindow class (DLWindow.py)
#      - MainWindows class (maps.py)
#
#  One of parameters query_region is callback function. Callback is used in
#  method query_tile()
#
#  function gui_callback from gtkThread.py is used as the callback.
#  Parameter to gui_callback is usually tile_received() implemented in
#  DLWindow.py and  maps.py. There is different behavior between DLWindow and
#  maps implementation of the method tile_received()
#
#  In short - query_tile() (usually) calls
#    - directly tile_received() implemented in DLWindow.py and maps.py
#      respectively or
#    - indirectly via DownloaderThread.process_task().
class MapDownloader:

    def __init__(self, ctx_map, numthreads=4):
        self.ctx_map = ctx_map
        self.threads = []
        self.bulk_all_placed = False
        self.taskq = Queue(0)
        self.queued = []
        for i in xrange(numthreads):
            t = DownloaderThread(self.ctx_map, self.taskq, self)
            self.threads.append(t)
            t.start()

    def __del__(self):
        self.stop_all()

    def wait_all(self):
        self.taskq.join()

    def stop_all(self):
        while not self.taskq.empty():
            self.taskq.get_nowait() # clear the queue
        for i in xrange(len(self.threads)):
            self.taskq.put(None) # put sentinels for threads
        for t in self.threads:
            print ".",
            t.join(0.1)
        self.threads = []
        self.queued = []

    def qsize(self):
        return self.taskq.qsize()

    # @return number of tiles queued for download
    def query_tile(self, coord, layer, callback,
                    online=True, force_update=False,
                    conf=None):
        ret = 0
        if (layer == LAYER_HYBRID):
            ret += self.query_tile(coord, LAYER_SATELLITE, callback, 
                                   online, force_update, conf)
        #print "query_tile(",coord,layer,callback,online,force_update,")"
        world_tiles = mapUtils.tiles_on_level(coord[2])
        coord = (mapUtils.mod(coord[0], world_tiles),
                 mapUtils.mod(coord[1], world_tiles), coord[2])
        # try to get a tile offline
        if self.ctx_map.is_tile_in_local_repos(coord, layer) or (not online):
            deleted = False
            if (force_update and online):
                deleted = self.ctx_map.remove_old_tile(coord, layer)
            if not deleted:
                callback(True, coord, layer)
                return ret

        if not (coord,layer) in self.queued:
            self.queued.append((coord, layer))
            self.taskq.put(
                DownloadTask(
                    coord, layer, callback, force_update, conf
                )
            )
        return ret + 1

    # @return number of tiles queued for download
    def query_region(self, xmin, xmax, ymin, ymax, zoom, *args, **kwargs):
        ret = 0
        world_tiles = mapUtils.tiles_on_level(zoom)
        if xmax-xmin >= world_tiles:
            xmin,xmax = 0,world_tiles-1
        if ymax-ymin >= world_tiles:
            ymin,ymax = 0,world_tiles-1
        #print "Query region",xmin,xmax,ymin,ymax,zoom
        for i in xrange((xmax-xmin+world_tiles)%world_tiles+1):
            x = (xmin+i)%world_tiles
            for j in xrange((ymax-ymin+world_tiles)%world_tiles+1):
                y = (ymin+j)%world_tiles
                ret += self.query_tile((x,y,zoom), *args, **kwargs)
        return ret

    # @return number of tiles queued for download
    def query_region_around_point(self, center, size, zoom, *args, **kwargs):
        x0, y0 = center[0][0], center[0][1]
        dx0, dy0 = int(center[1][0] - size[0]/2), int(center[1][1] - size[1]/2)
        dx1, dy1 = dx0+size[0], dy0+size[1]
        xmin = int(x0 + floor(dx0/TILES_WIDTH))
        xmax = int(x0 + ceil(dx1/TILES_WIDTH)) - 1
        ymin = int(y0 + floor(dy0/TILES_HEIGHT))
        ymax = int(y0 + ceil(dy1/TILES_HEIGHT)) - 1
        return self.query_region(xmin, xmax, ymin, ymax, zoom, *args, **kwargs)

    def query_region_around_location(self, lat0, lon0, dlat, dlon, zoom,
                                        *args, **kwargs):
        if dlat > 170:
            lat0 = 0
            dlat = 170
        if dlon > 358:
            lon0 = 0
            dlon = 358

        top_left = mapUtils.coord_to_tile(
            (lat0+dlat/2, lon0-dlon/2, zoom)
        )
        bottom_right = mapUtils.coord_to_tile(
            (lat0-dlat/2, lon0+dlon/2, zoom)
        )
        self.query_region(top_left[0][0], bottom_right[0][0],
                          top_left[0][1], bottom_right[0][1],
                          zoom, *args, **kwargs)

    def bulk_download(self, coord, zoomlevels, kmx, kmy, layer, tile_callback,
                      completion_callback, force_update=False, conf=None,
                      nodups=True):
        dlon = mapUtils.km_to_lon(mapUtils.nice_round(kmx), coord[0])
        dlat = mapUtils.km_to_lat(mapUtils.nice_round(kmy))
        if zoomlevels[0] > zoomlevels[1]:
            zoomlevels = (zoomlevels[1], zoomlevels[0])

        def downThread():
            self.bulk_all_placed = False
            for zoom in xrange(zoomlevels[1], zoomlevels[0] - 1, -1):
                self.query_region_around_location(
                    coord[0], coord[1], dlat, dlon,
                    zoom, layer, tile_callback, True,
                    force_update, conf
                    )
            if self.qsize() == 0:
                completion_callback()
            self.bulk_all_placed = True


        dThread = Timer(0, downThread)
        dThread.start()
