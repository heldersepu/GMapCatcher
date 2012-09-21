## @package gmapcatcher.tilesRepoSQLite3
# This modul provides sqlite3 tile repository functions
#
# Usage:
#
# - constructor requires MapServ instance, because method
#  'get_tile_from_coord' is provided in the MapServ
#


import os
import gtk
import sys
import time
import sqlite3
import threading
import traceback

import gmapcatcher.lrucache as lrucache
import gmapcatcher.mapPixbuf as mapPixbuf
from threading import Lock, Thread
from gmapcatcher.mapConst import *


class tilesReposSQLiteException(Exception):
    pass


class tilesReposSQLiteInvalidPathException(tilesReposSQLiteException):
    pass


class tileNotInRepository(Exception):
    pass

SQL_IDX_X = 0
SQL_IDX_Y = 1
SQL_IDX_ZOOM = 2
SQL_IDX_LAYER = 3
SQL_IDX_TSTAMP = 4
SQL_IDX_IMG = 5
SQL_DATABASE_DDL = "CREATE TABLE tiles (x INTEGER, y INTEGER,zoom INTEGER,layer INTEGER, tstamp INTEGER, img BLOB, PRIMARY KEY(x,y,zoom,layer));"
"""
Another not used DDL:
CREATE TABLE maps (id INTEGER, name TEXT, zoom TEXT, type INTEGER, PRIMARY KEY(id));
CREATE TABLE regions_points (regionsid INTEGER, lat REAL,lon REAL, pos INTEGER,
PRIMARY KEY(regionsid,lat,lon));
CREATE TABLE map_regions (regionsid INTEGER, mapid INTEGER, PRIMARY KEY(regionsid));
"""

from tilesRepo import TilesRepository


class SQLite3Thread(Thread):

    def __init__(self, url_dir, url_filename):
        Thread.__init__(self)

        self.dburl = os.path.join(url_dir, url_filename)
        self.dbconn = None
        self.dbcurs = None
        self.sql_request = None
        self.sql_response = None
        self.finish_flag = False

        self.event = threading.Event()
        self.thlock = threading.Lock()
        self.resplock = threading.Lock()
        self.respcond = threading.Condition(self.resplock)

        if not os.path.isdir(url_dir):
            os.makedirs(url_dir)

    def run(self):
        while True:
            self.event.wait()

            if self.finish_flag:
                if not self.dbconn is None:
                    self.dbconn.close()
                self.event.clear()
                return True

            self.event.clear()

            self.process_sqlrequest()
            self.respcond.acquire()
            self.respcond.notify()
            self.respcond.release()

    def event_clear(self):
        self.event.clear()

    def event_set(self):
        self.event.set()

    def finish_thread(self):
        self.finish_flag = True
        self.event.set()

    def process_sqlrequest(self):
        #print "D:process_sqlrequest: " + str(thread.get_ident())
        if not self.sql_request is None:
            req = self.sql_request[1]

            if self.sql_request[0] == "store_tile":
                self.store_tile(req[0], req[1], req[2], req[3], req[4])

            elif self.sql_request[0] == "get_tile_row":
                self.get_tile_row(req[0], req[1], req[2], req[3])

            elif self.sql_request[0] == "delete_tile":
                self.delete_tile(req[0], req[1], req[2])

            self.sql_request = None

    def dbconnection(self):
        if self.dbconn is None:
            #print "D:sqlite3.connect( url ): " + str(thread.get_ident())
            createTable = False
            if(not os.path.isfile(self.dburl)):
                createTable = True
            self.dbconn = sqlite3.connect(self.dburl)
            self.dbcurs = self.dbconn.cursor()
            if createTable:
                #process create table
                dbcursor = self.dbcoursor()
                dbcursor.execute(SQL_DATABASE_DDL)
                self.dbconn.commit()
        return self.dbconn

    def dbcoursor(self):
        self.dbconnection()
        return self.dbcurs

    def get_tile_row(self, layer, zoom_level, coord, olderthan):
        if(olderthan == -1):
            qry = "SELECT  x,y,zoom,layer, tstamp, img FROM tiles WHERE zoom=%i AND x=%i AND y=%i AND layer=%i" % (zoom_level, coord[0], coord[1], layer)
        else:
            qry = "SELECT  x,y,zoom,layer, tstamp, img FROM tiles WHERE zoom=%i AND x=%i AND y=%i AND layer=%i AND tstamp<%i" % (zoom_level, coord[0], coord[1], layer, olderthan)
        dbcursor = self.dbcoursor()
        dbcursor.execute(qry)
        self.sql_response = dbcursor.fetchone()

    def store_tile(self, layer, zoom_level, coord, tstamp, data):
        try:
            dbcursor = self.dbcoursor()
            dbcursor.execute("INSERT INTO tiles (x,y,zoom,layer,tstamp,img)  VALUES(?,?,?,?,?,?)", (coord[0], coord[1], zoom_level, layer, tstamp, sqlite3.Binary(data)))
            self.dbconnection().commit()
        except sqlite3.IntegrityError:
            # Known problem - one tile is downloaded more than once, when tile is:
            #    - scheduled for download
            #    - mouse moves map in the window
            #    - in such case missing tiles are again scheduled for donwload
            # ToDo: - solution: maintain queue tiles scheduled for download
            ei = sys.exc_info()
            print traceback.format_exception(ei[0], ei[1], ei[2])
            #print "Debug: " + str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            #pass

    def delete_tile(self, layer, zoom_level, coord):
        qry = "DELETE FROM tiles WHERE zoom=%i AND x=%i AND y=%i AND layer=%i" % (zoom_level, coord[0], coord[1], layer)
        dbcursor = self.dbcoursor()
        dbcursor.execute(qry)
        self.dbconnection().commit()

    def set_sql_request(self, req):
        self.sql_request = [req[0], req[1]]

    def get_sql_response(self):
        resp = self.sql_response
        self.sql_response = None
        return resp


class SQLite3Funcs():

    def __init__(self, url_dir, url_filename):
        self.url = os.path.join(url_dir, url_filename)
        self.sql_thread = None

        if self.sql_thread is None:
            self.sql_thread = SQLite3Thread(url_dir, url_filename)

        if not self.sql_thread.isAlive():
            self.sql_thread.start()

    def finish(self):
        if self.sql_thread is None:
            return
        self.sql_thread.finish_thread()
        self.sql_thread.join()
        self.sql_thread = None

    def restart_thread(self, url_dir, url_filename):
        if self.sql_thread is not None:
            if self.sql_thread.isAlive():
                self.sql_thread.finish_thread()
                self.sql_thread.join()
                self.sql_thread = None

        self.sql_thread = SQLite3Thread(url_dir, url_filename)
        self.sql_thread.start()

    # coord is [x,y]
    def get_tile_row(self, layer, zoom_level, coord, olderthan=-1):
        try:
            self.sql_thread.thlock.acquire()
            self.sql_thread.respcond.acquire()

            req = ("get_tile_row", (layer, zoom_level, coord, olderthan))
            self.sql_thread.set_sql_request(req)
            self.sql_thread.event_set()
            self.sql_thread.respcond.wait()
            self.sql_thread.respcond.release()
            resp = self.sql_thread.get_sql_response()
        finally:
            self.sql_thread.thlock.release()

        return resp

    def store_tile(self, layer, zoom_level, coord, tstamp, data):
        try:
            self.sql_thread.thlock.acquire()
            self.sql_thread.respcond.acquire()

            req = ("store_tile", (layer, zoom_level, coord, tstamp, data))
            self.sql_thread.set_sql_request(req)
            self.sql_thread.event_set()
            self.sql_thread.respcond.wait()
            self.sql_thread.respcond.release()
        finally:
            self.sql_thread.thlock.release()

        return

    def delete_tile(self, layer, zoom_level, coord):
        try:
            self.sql_thread.thlock.acquire()
            self.sql_thread.respcond.acquire()

            req = ("delete_tile", (layer, zoom_level, coord))
            self.sql_thread.set_sql_request(req)
            self.sql_thread.event_set()
            self.sql_thread.respcond.wait()
            self.sql_thread.respcond.release()
            resp = self.sql_thread.get_sql_response()
        finally:
            self.sql_thread.thlock.release()

        return resp


class TilesRepositorySQLite3(TilesRepository):

    def __init__(self, MapServ_inst, conf):
        TilesRepository.__init__(self, MapServ_inst, conf)
        self.tile_cache = lrucache.LRUCache(1000)
        self.mapServ_inst = MapServ_inst
        self.configpath = conf.init_path
        self.lock = Lock()
        self.missingPixbuf = mapPixbuf.missing()
        self.sqlite3func = SQLite3Funcs(self.configpath, SQLITE3_REPOSITORY_FILE)

    def finish(self):
        self.sqlite3func.finish()
        # last command in finish
        TilesRepository.finish(self)

    ## Sets new repository path to be used for storing tiles
    def set_repository_path(self, newpath):
        self.sqlite3func.restart_thread(newpath, SQLITE3_REPOSITORY_FILE)

    ## Returns the PixBuf of the tile
    # Uses a cache to optimise HDD read access
    # PUBLIC
    def load_pixbuf(self, coord, layer, force_update):
        filename = self.coord_to_path(coord, layer)
        if (not force_update) and (filename in self.tile_cache):
            pixbuf = self.tile_cache[filename]
        else:
            #
            dbrow = self.sqlite3func.get_tile_row(layer, coord[2], (coord[0], coord[1]))
            if dbrow is None:
                pixbuf = self.missingPixbuf
            else:
                try:
                    pixbuf = self.create_pixbuf_from_data(dbrow[SQL_IDX_IMG])
                    self.tile_cache[filename] = pixbuf
                except:
                    pixbuf = self.missingPixbuf

        return pixbuf

    # PUBLIC
    def remove_old_tile(self, coord, layer, filename=None, intSeconds=86400):
        """not used anymore?! don't know about it. But repoFS and repoMGMaps got rid of this
        methods.
        """
        dbrow = self.sqlite3func.get_tile_row(layer, coord[2], (coord[0], coord[1]))

        # TODO: should be OK, but test properly
        if dbrow[SQL_IDX_TSTAMP] >= (int(time.time()) - intSeconds):
            try:
                if filename is None:
                    filename = self.coord_to_path(coord, layer)
                self.tile_cache[filename] = self.create_pixbuf_from_data(dbrow[SQL_IDX_IMG])
            except:
                pass
            return False

        try:
            if filename is None:
                filename = self.coord_to_path(coord, layer)
            del self.tile_cache[filename]
        except KeyError:
            pass

        return True

    # PUBLIC
    def is_tile_in_local_repos(self, coord, layer):
        filename = self.coord_to_path(coord, layer)
        if filename in self.tile_cache:
            return True
        dbrow = self.sqlite3func.get_tile_row(layer, coord[2], (coord[0], coord[1]))
        if dbrow is None:
            return False
        else:
            return True

    def create_pixbuf_from_data(self, data):
        # Default result to the "data" buffer
        pixbuf = data
        try:
            loader = gtk.gdk.PixbufLoader()
            loader.write(data)
            loader.close()
            pixbuf = loader.get_pixbuf()
        except:
            #print traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            raise
        return pixbuf

    ## Get the png file for the given location
    # Returns true if the file is successfully retrieved
    # private
    def get_png_file(self, coord, layer, online, force_update, conf):
        # remove tile only when online
        filename = self.coord_to_path(coord, layer)
        if (force_update and online):
            # force update = delete tile from repository and download new version
            #self.remove_old_tile(coord, layer, filename)
            # if in remove_old_tile tile_cache is populated if tile is not too old
            if filename in self.tile_cache:
                del self.tile_cache[filename]

        else:
            # we don't have to download tile from internet
            if filename in self.tile_cache:
                return True

            dbrow = self.sqlite3func.get_tile_row(layer, coord[2], (coord[0], coord[1]))
            if dbrow is not None:
                try:
                    self.tile_cache[filename] = self.create_pixbuf_from_data(dbrow[5])
                except:
                    pass
                return True

        if not online:
            return False

        # download data
        try:
            oa_data = self.mapServ_inst.get_tile_from_coord(coord, layer, conf)
            try:
                self.tile_cache[filename] = self.create_pixbuf_from_data(dbrow[SQL_IDX_IMG])
            except:
                pass
            self.sqlite3func.store_tile(layer, coord[2], (coord[0], coord[1]), int(time.time()), oa_data)
            return True

        except KeyboardInterrupt:
            raise
        except:
            ei = sys.exc_info()
            print '\tdownload failed -' + str(traceback.format_exception(ei[0], ei[1], ei[2], None))
        return False

    def get_plain_tile(self, coord, layer):
        dbrow = self.sqlite3func.get_tile_row(layer, coord[2], (coord[0], coord[1]))
        if dbrow is not None:
            return dbrow[5]
        raise tileNotInRepository(str((coord, layer)))

    def store_plain_tile(self, coord, layer, tiledata):
        if self.is_tile_in_local_repos(coord, layer):
            self.sqlite3func.delete_tile(layer, coord[2], (coord[0], coord[1]))
        self.sqlite3func.store_tile(layer, coord[2], (coord[0], coord[1]), int(time.time()), tiledata)

    ## Return the absolute path to a tile
    #  only check path
    #  tile_coord = (tile_X, tile_Y, zoom_level)
    #  smaple of the Naming convention:
    #  \.googlemaps\tiles\15\0\1\0\1.png
    #  We only have 2 levels for one axis
    #  at most 1024 files in one dir
    # private
    def coord_to_path(self, tile_coord, layer):
        path = os.path.join(self.configpath,
                            LAYER_DIRS[layer],
                            str('%d' % tile_coord[2]),
                            str(tile_coord[0] / 1024),
                            str(tile_coord[0] % 1024),
                            str(tile_coord[1] / 1024),
                            str(tile_coord[1] % 1024) + ".png"
                            )
        return path
