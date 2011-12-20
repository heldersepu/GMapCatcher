# -*- coding: utf-8 -*-
## @package gmapcatcher.tilesRepoFactory
# Place to set the correct repository

import sys
import mapConst
import tilesRepoFS
import tilesRepoMGMaps
import tilesRepoSQLite3
import tilesRepoOSM

# list of instantiated repositories
repositories = []

class repositoryNotCreatedError(Exception):
    pass

# creates new repository with given path and type
# public static
def get_tile_repository(mapservice, configpath, tilerepostype):

    repos = pick_repository_from_list(configpath, tilerepostype)

    if repos is None:
        repos = create_repos_inst(mapservice, configpath, tilerepostype)
        append_repository_to_list(repos, configpath, tilerepostype)

    return repos


def append_repository_to_list( repos, configpath, tilerepostype ):
    global repositories
    repos_entry = { "repos": repos, "configpath": configpath, "type": tilerepostype }
    repositories.append( repos_entry )
    return True

def pick_repository_from_list( configpath, tilerepostype ):
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
            if rep["configpath"] == configpath and rep["type"] == tilerepostype:
                found_repos = rep["repos"]
                # we don't exit here, because we want to walk over all repository entries in list
                # to remove finished

        idx = idx + 1

    return found_repos


# private static
def create_repos_inst(mapservice, configpath, repo_type):
    if repo_type == mapConst.REPOS_TYPE_SQLITE3:
        repository_inst = tilesRepoSQLite3.TilesRepositorySQLite3(mapservice, configpath)

    elif repo_type == mapConst.REPOS_TYPE_MGMAPS:
        repository_inst = tilesRepoMGMaps.TilesRepositoryMGMaps(mapservice, configpath)

    elif repo_type == mapConst.REPOS_TYPE_OSM:
        repository_inst = tilesRepoOSM.TilesRepositoryOSM(mapservice, configpath)

    else: # repo_type == mapConst.REPOS_TYPE_FILES
        repository_inst = tilesRepoFS.TilesRepositoryFS(mapservice, configpath)

    if repository_inst is None:
        raise repositoryNotCreatedError(str( (configpath, repo_type) ))

    return repository_inst


