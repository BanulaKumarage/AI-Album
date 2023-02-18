import pathlib
import logging
import glob
from typing import Optional

import networkx as nx
from bson import ObjectId

from server.db import async_client


LOG = logging.getLogger(__name__)
DAG_ROOT = "R"


def record_album(name: str, path: str, parent: list[str]) -> ObjectId:
    document = {
        "name": name,
        "directory": path,
        "parentAlbumIds": parent,
    }

    result = async_client.ai_album.albums.update_one(
        {"directory": path}, {"$setOnInsert": document}, upsert=True
    )
    if result.upserted_id:
        LOG.debug(f'Added album "{result.upserted_id}" as child of "{parent}"')
        return result.upserted_id
    else:
        result = async_client.ai_album.albums.find_one({"directory": path})
        return result["_id"]


def record_media(name: str, path: str, album_ids: list[str]) -> None:
    document = {
        "name": name,
        "path": path,
        "albumIds": album_ids,
    }
    result = async_client.ai_album.media.update_one(
        {"path": path}, {"$setOnInsert": document}, upsert=True
    )
    if result.upserted_id:
        LOG.debug(f'Added media "{name}" for albums "{album_ids}" from path "{path}"')


def init_path_graph():
    pg = nx.DiGraph()
    pg.add_node(DAG_ROOT, id=None, path="")
    return pg


def run_indexing(dir):
    LOG.debug("Start indexing files")
    LOG.debug(f"Traversing {dir}/data")
    pg = init_path_graph()
    data_path = f"{dir}/data/"

    # iterat all files in thee destination
    for file in glob.iglob(f"{data_path}/**", recursive=True):
        file = pathlib.Path(file)
        if not file.is_file():
            continue

        resource_path = file.relative_to(data_path)
        resource_path_parts = resource_path.parts

        path_parts = resource_path_parts[:-1]
        resource_name = resource_path_parts[-1]

        # record unfoldered files without a parent album
        if len(path_parts) == 0 and len(resource_name) != 0:
            record_media(resource_name, resource_path.as_posix(), [])

        # files nested within folders
        elif len(path_parts) != 0 and len(resource_name) != 0:
            # if first part was not recorded as an album, this is a new sub-folder
            if not pg.has_successor(DAG_ROOT, f"{DAG_ROOT}/{path_parts[0]}"):
                # recreate the who DAG
                pg = init_path_graph()
                last_node = DAG_ROOT

                # record each foldre as an album (recursive folder adding)
                for itr_part in path_parts:
                    part = f"{last_node}/{itr_part}"
                    # updat DAG
                    pg.add_node(part)
                    pg.add_edge(last_node, part)
                    pg.nodes[part][
                        "path"
                    ] = f'{pg.nodes[last_node]["path"]}/{itr_part}'.lstrip("/")
                    pg.nodes[part]["id"] = record_album(
                        itr_part,
                        pg.nodes[part]["path"],
                        [
                            pg.nodes[p]["id"]
                            for p in pg.nodes()
                            if p != DAG_ROOT and p != part
                        ],
                    )
                    last_node = part
            else:
                # not a new subfolder, so start with DAG_ROOT
                last_node = DAG_ROOT

                for part in path_parts:
                    part = f"{last_node}/{part}"
                    # if the part is already recorded, nothing to do
                    if pg.has_successor(last_node, part):
                        last_node = list(pg.neighbors(last_node))[0]
                        continue

                    # if not, we are are branching, so remove all the subsequent nodes (they are irrelevant)
                    removables = list(nx.dfs_preorder_nodes(pg, last_node))[1:]
                    for r in removables:
                        pg.remove_node(r)

                    break

                last_node = DAG_ROOT

                # we are recording the new brach
                for itr_part in path_parts:
                    part = f"{last_node}/{itr_part}"
                    # just ignoring the branches we already recordeed
                    if pg.has_successor(last_node, part):
                        last_node = list(pg.neighbors(last_node))[0]
                        continue
                    # now we are at the unrecorded part (or we have broken out of the loop)
                    # so we record a new album just like we did before
                    pg.add_node(part)
                    pg.add_edge(last_node, part)
                    pg.nodes[part][
                        "path"
                    ] = f'{pg.nodes[last_node]["path"]}/{itr_part}'.lstrip("/")
                    pg.nodes[part]["id"] = record_album(
                        itr_part,
                        pg.nodes[part]["path"],
                        [
                            pg.nodes[p]["id"]
                            for p in pg.nodes()
                            if p != DAG_ROOT and p != part
                        ],
                    )
            # record the media, with the entire album tree
            record_media(
                resource_name,
                resource_path.as_posix(),
                [pg.nodes[p]["id"] for p in pg.nodes() if p != DAG_ROOT],
            )
    LOG.debug("Finish indexing files")
