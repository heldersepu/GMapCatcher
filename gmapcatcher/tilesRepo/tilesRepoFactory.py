# -*- coding: utf-8 -*-
## @package gmapcatcher.tilesRepoFactory
# Place to set the correct repository

import tilesRepoFS
import tilesRepoMGMaps
import tilesRepoSQLite3
import tilesRepoOSM
import tilesRepoRMaps
from gmapcatcher.mapConst import *

# list of instantiated repositories
repositories = []

# creates new repository with given path and type
# public static
def get_tile_repository(mapservice, conf):
    repos = pick_repository_from_list(conf)
    if repos is None:
        repos = create_repos_inst(mapservice, conf)
        append_repository_to_list(repos, conf)
    return repos

def append_repository_to_list(repos, conf):
    global repositories
    repos_entry = {"repos": repos, "configpath": conf.init_path, "type": tilerepostype}
    repositories.append(repos_entry)
    return True

def pick_repository_from_list(conf):
    """returns instance of repository from list or None"""
    global repositories
    found_repos = None
    idx = 0
    for rep in repositories[:]:
        if rep["repos"].is_finished():
            del repositories[idx]
            # we are removing repository, so what was rep[idx+2] before deleting rep[idx], is rep[idx+1] after deleting.
            idx = idx - 1
        else:
            if rep["configpath"] == conf.init_path and rep["type"] == conf.repository_type:
                found_repos = rep["repos"]
                # we don't exit here, because we want to walk over all repository entries in list
                # to remove finished
        idx = idx + 1
    return found_repos

# private static
def create_repos_inst(mapservice, conf):
    if conf.repository_type == REPOS_TYPE_SQLITE3:
        return tilesRepoSQLite3.TilesRepositorySQLite3(mapservice, conf)

    elif conf.repository_type == REPOS_TYPE_MGMAPS:
        return tilesRepoMGMaps.TilesRepositoryMGMaps(mapservice, conf)

    elif conf.repository_type == REPOS_TYPE_OSM:
        return tilesRepoOSM.TilesRepositoryOSM(mapservice, conf)

    elif conf.repository_type == REPOS_TYPE_RMAPS:
        return tilesRepoRMaps.TilesRepositoryRMaps(mapservice, conf)

    else:  # conf.repository_type == REPOS_TYPE_FILES
        return tilesRepoFS.TilesRepositoryFS(mapservice, conf)
