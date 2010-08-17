## @package gmapcatcher.tilesRepoSQLite3
# This modul provides sqlite3 tile repository functions
#
# Usage:
#
# - constructor requires MapServ instance, because method
#  'get_tile_from_coord' is provided in the MapServ
#
# - this module is not used directly. It is used via MapServ() methods:
#    def finish(self):
#    def load_pixbuf(self, coord, layer, force_update):
#    def do_export(self, tcoord, layer, online, mapServ, styleID, size):
#    def remove_old_tile(self, coord, layer, filename=None, interval=86400):
#    def is_tile_in_local_repos(self, coord, layer):
#    def set_repository_path(self, newpath):
# - module is finalized from MapServ.finish() method


import os
import sys
import gtk
import time

import lrucache
import mapPixbuf
import fileUtils

import sqlite3
import threading
import logging
import traceback

from threading import Lock, Thread
from mapConst import *


class tilesReposSQLiteException(Exception):
    pass

class tilesReposSQLiteInvalidPathException(tilesReposSQLiteException):
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

    def __init__(self, url):
        Thread.__init__(self)

        self.dburl = None
        self.dbconn = None
        self.dbcurs = None
        self.sql_request = None
        self.sql_response = None
        self.finish_flag = False


        self.event = threading.Event()
        self.thlock = threading.Lock()
        self.resplock = threading.Lock()
        self.respcond = threading.Condition(self.resplock)

        self.dburl = url
        logging.debug("SQLite3Thread initializing instance %s" % (url, ) )


    def run(self):

        while True:
            self.event.wait()

            if self.finish_flag:
                logging.debug("SQLite3Thread leaving method run")
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
        logging.debug("SQLite3Thread setting finish flag")
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
            logging.debug("Connecting to db: " + self.dburl)
            createTable = False
            if(not os.path.isfile(self.dburl)):
                createTable = True
            self.dbconn = sqlite3.connect( self.dburl )
            self.dbcurs = self.dbconn.cursor()
            if createTable:
                #process create table
                dbcursor = self.dbcoursor()
                dbcursor.execute( SQL_DATABASE_DDL )
                self.dbconn.commit()
        return self.dbconn

    def dbcoursor(self):
        self.dbconnection()
        return self.dbcurs

    def get_tile_row(self, layer, zoom_level, coord, olderthan ):
        if(olderthan == -1):
            qry = "SELECT  x,y,zoom,layer, tstamp, img FROM tiles WHERE zoom=%i AND x=%i AND y=%i AND layer=%i" % (zoom_level, coord[0], coord[1], layer)
        else:
            qry = "SELECT  x,y,zoom,layer, tstamp, img FROM tiles WHERE zoom=%i AND x=%i AND y=%i AND layer=%i AND tstamp<%i" % (zoom_level, coord[0], coord[1], layer, olderthan)
        logging.debug("Executing query: " + qry)
        dbcursor = self.dbcoursor()
        dbcursor.execute( qry )
        self.sql_response = dbcursor.fetchone()

    def store_tile(self, layer, zoom_level, coord, tstamp, data):
        qry = "INSERT INTO tiles (x,y,zoom,layer,tstamp,img)  VALUES(%i,%i,%i,%i,%i,%s)" % (coord[0], coord[1],zoom_level,layer,tstamp,"img")
        logging.debug("Executing query: " + qry)
        try:
            dbcursor = self.dbcoursor()
            dbcursor.execute( "INSERT INTO tiles (x,y,zoom,layer,tstamp,img)  VALUES(?,?,?,?,?,?)", (coord[0], coord[1],zoom_level,layer,tstamp,sqlite3.Binary(data)) )
            self.dbconnection().commit()
        except sqlite3.IntegrityError:
            # currently - one tile is downloaded more than one, when tile is:
            #    - scheduled for donwload
            #    - mouse moves map in the window
            #    - in such case missing tiles are again scheduled for donwload
            # ToDo: - solution: maintain queue tiles scheduled for download
            logging.error( traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]) )
            print "Debug: " + str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            pass

    def delete_tile(self, layer, zoom_level, coord):
        qry = "DELETE FROM tiles WHERE zoom=%i AND x=%i AND y=%i AND layer=%i" % (zoom_level, coord[0], coord[1], layer)
        logging.debug("Executing query: " + qry)
        dbcursor = self.dbcoursor()
        dbcursor.execute( qry )
        self.dbconnection().commit()


    def set_sql_request(self, req):
        self.sql_request = [ req[0], req[1] ]

    def get_sql_response(self):
        resp = self.sql_response
        self.sql_response = None
        return resp


class SQLite3Funcs():

    def __init__(self, url):
        logging.debug("Starting SQLite3Thread")

        self.sql_thread = None

        if self.sql_thread is None:
            self.sql_thread = SQLite3Thread( url )

        if not self.sql_thread.isAlive():
            self.sql_thread.start()


    def finish(self):
        logging.debug("SQLite3Funcs finish started")
        self.sql_thread.finish_thread()
        logging.debug("SQLite3Funcs joining SQLite3Thread...")
        self.sql_thread.join()
        logging.debug("SQLite3Funcs joined.")
        self.sql_thread = None


    def restart_thread(self, url):

        if self.sql_thread is not None:
            if not self.sql_thread.isAlive():
                logging.debug("SQLite3Funcs finish started")
                self.sql_thread.finish_thread()
                logging.debug("SQLite3Funcs joining SQLite3Thread...")
                self.sql_thread.join()
                logging.debug("SQLite3Funcs joined.")
                self.sql_thread = None

        self.sql_thread = SQLite3Thread( url )
        self.sql_thread.start()


    # coord is [x,y]
    def get_tile_row(self, layer, zoom_level, coord, olderthan=-1 ):
        try:
            self.sql_thread.thlock.acquire()
            self.sql_thread.respcond.acquire()

            req = ("get_tile_row", (layer, zoom_level, coord, olderthan) )
            self.sql_thread.set_sql_request( req )
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

            req = ("store_tile", (layer, zoom_level, coord, tstamp, data) )
            self.sql_thread.set_sql_request( req )
            self.sql_thread.event_set()
            self.sql_thread.respcond.wait()
            self.sql_thread.respcond.release()
            resp = self.sql_thread.get_sql_response()
        finally:
            self.sql_thread.thlock.release()

        return

    def delete_tile(self, layer, zoom_level, coord):
        try:
            self.sql_thread.thlock.acquire()
            self.sql_thread.respcond.acquire()

            req = ("delete_tile", (layer, zoom_level, coord) )
            self.sql_thread.set_sql_request( req )
            self.sql_thread.event_set()
            self.sql_thread.respcond.wait()
            self.sql_thread.respcond.release()
            resp = self.sql_thread.get_sql_response()
        finally:
            self.sql_thread.thlock.release()

        return resp



class TilesRepositorySQLite3(TilesRepository):

    def __init__(self, MapServ_inst):
        self.tile_cache = lrucache.LRUCache(1000)
        self.mapServ_inst = MapServ_inst
        self.lock = Lock()

        self.missingPixbuf = mapPixbuf.missing()

        # path self.mapServ_inst.configpath points to the directory where database file is stored
        self.sqlite3func = SQLite3Funcs( os.path.join(self.mapServ_inst.configpath, SQLITE3_REPOSITORY_FILE) )



    def finish(self):
        self.sqlite3func.finish()

    ## Sets new repository path to be used for storing tiles
    def set_repository_path(self, newpath):
        self.sqlite3func.restart_thread( os.path.join(newpath, SQLITE3_REPOSITORY_FILE) )

    ## Returns the PixBuf of the tile
    # Uses a cache to optimise HDD read access
    # PUBLIC
    def load_pixbuf(self, coord, layer, force_update):
        filename = self.coord_to_path(coord, layer)
        if not force_update and (filename in self.tile_cache):
            pixbuf = self.tile_cache[filename]
        else:
            #
            dbrow = self.sqlite3func.get_tile_row(MAP_SERVICES[layer]["ID"], coord[2], (coord[0],coord[1]) )
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
        dbrow = self.sqlite3func.get_tile_row(type, coord[2], (coord[0],coord[1]) )

        # TODO: should be OK, but test properly
        if dbrow[SQL_IDX_TSTAMP] >= (int( time.time() ) - intSeconds):
            try:
                if filename is None:
                    filename = self.coord_to_path(coord, layer)
                self.tile_cache[ filename ] = self.create_pixbuf_from_data( dbrow[SQL_IDX_IMG] )
            except:
                pass
            return False

        dbres = self.sqlite3func.delete_tile(type, coord[2], (coord[0],coord[1]) )
        a = dbres
        try:
            if filename is None:
                filename = self.coord_to_path(coord, layer)
            del self.tile_cache[ filename ]
        except KeyError:
            pass

        return True


    # PUBLIC
    def is_tile_in_local_repos(self, coord, layer):
        dbrow = self.sqlite3func.get_tile_row(MAP_SERVICES[layer]["ID"], coord[2], (coord[0],coord[1]) )
        if dbrow is None:
            return False
        else:
            return True

    def create_pixbuf_from_data(self, data):
        try:
            loader = gtk.gdk.PixbufLoader()
            loader.write( data )
            loader.close()

            pixbuf = loader.get_pixbuf()

        except:
            print traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            logging.error( traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]) )
            raise
        return pixbuf


    ## Get the png file for the given location
    # Returns true if the file is successfully retrieved
    # private
    def get_png_file(self, coord, layer, online, force_update, conf):
        # remove tile only when online
        filename = self.coord_to_path(coord, layer)
        if (force_update and online):
            self.remove_old_tile(coord, layer, filename)
            # if in remove_old_tile tile_cache is populated if tile is not too old
            if self.tile_cache.has_key(filename):
                return True

        dbrow = self.sqlite3func.get_tile_row(MAP_SERVICES[layer]["ID"], coord[2], (coord[0],coord[1]) )
        if dbrow is not None:
            try:
                self.tile_cache[filename] = self.create_pixbuf_from_data(dbrow[5])
            except:
                pass
            return True

        if not online:
            return False


        # donwload data
        try:
            oa_data = self.mapServ_inst.get_tile_from_coord(coord, layer, conf)
            logging.debug("Storing tile into DB: %i, %i, xy: %i, %i" % (MAP_SERVICES[layer]["ID"], coord[2], coord[0], coord[1]) )
            try:
                self.tile_cache[filename] = self.create_pixbuf_from_data(dbrow[SQL_IDX_IMG])
            except:
                pass
            self.sqlite3func.store_tile( MAP_SERVICES[layer]["ID"], coord[2], (coord[0], coord[1]), int( time.time() ), oa_data )
            return True

        except KeyboardInterrupt:
            raise
        except:
            print '\tdownload failed -', sys.exc_info()[0]
        return False

    ## Return the absolute path to a tile
    #  only check path
    #  tile_coord = (tile_X, tile_Y, zoom_level)
    #  smaple of the Naming convention:
    #  \.googlemaps\tiles\15\0\1\0\1.png
    #  We only have 2 levels for one axis
    #  at most 1024 files in one dir
    # private
    def coord_to_path(self, tile_coord, layer):
        path = os.path.join(self.mapServ_inst.configpath,
                            MAP_SERVICES[layer]["layerDir"],
                            str('%d' % tile_coord[2]),
                            str(tile_coord[0] / 1024),
                            str(tile_coord[0] % 1024),
                            str(tile_coord[1] / 1024),
                            str(tile_coord[1] % 1024) + ".png"
                            )
        return path
