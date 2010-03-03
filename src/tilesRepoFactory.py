'''
Created on Feb 28, 2010

@author: standa

'''

import sys
import mapConst
import tilesRepoFS
import tilesRepoSQLite3


_repository_inst = None
_repository_path = None
_repository_type = None

# creates new repository with given path and type
# public static
def get_tile_repository(mapservice, configpath, tilerepostype):
    global _repository_inst
    global _repository_path
    global _repository_type


    if _repository_path == configpath and _repository_type == tilerepostype and _repository_inst is not None:
        return _repository_inst



    if _repository_inst is not None:

        if _repository_type == tilerepostype:
            _repository_path = configpath
            print "Setting new repository path: " + configpath + " for type: " + str(tilerepostype)
            _repository_inst.set_repository_path(configpath)
            return _repository_inst

        _repository_inst.finish()
        _repository_inst = None


    _repository_type = tilerepostype
    create_repos_inst(mapservice)
    _repository_path = configpath

    return _repository_inst

# private static
def create_repos_inst(mapservice):
    global _repository_inst
    global _repository_path
    global _repository_type

    if _repository_type == mapConst.ROPES_TYPE_FILES:
        _repository_inst = tilesRepoFS.TilesRepositoryFS(mapservice)

    elif _repository_type == mapConst.ROPES_TYPE_SQLITE3:
        _repository_inst = tilesRepoSQLite3.TilesRepositorySQLite3(mapservice)

    else:
        _repository_inst = tilesRepoFS.TilesRepositoryFS(mapservice)


