# -*- coding: utf-8 -*-
## @package gmapcatcher.tilesRepoFactory
# Place to set the correct repository

import sys
import logging
log = logging.getLogger(__name__)
import mapConst
import tilesRepoFS
import tilesRepoMGMaps
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
    create_repos_inst(mapservice, tilerepostype)
    _repository_path = configpath

    return _repository_inst

# private static
def create_repos_inst(mapservice, repo_type):
    global _repository_inst

    if repo_type == mapConst.REPOS_TYPE_SQLITE3:
        _repository_inst = tilesRepoSQLite3.TilesRepositorySQLite3(mapservice)
    
    elif repo_type == mapConst.REPOS_TYPE_MGMAPS:
        _repository_inst = tilesRepoMGMaps.TilesRepositoryMGMaps(mapservice)
    
    else: # repo_type == mapConst.REPOS_TYPE_FILES
        _repository_inst = tilesRepoFS.TilesRepositoryFS(mapservice)


