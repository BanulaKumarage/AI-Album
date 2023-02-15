import pathlib
import logging
import glob
from typing import Optional

import networkx as nx
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from server.db import async_client


LOG = logging.getLogger(__name__)
DAG_ROOT = "R"


def record_album(path: str, parent: Optional[str]) -> ObjectId:
    document = {
        "name": path,
        "directory": path,
        "parentAlbum": parent,
    }

    result = async_client.ai_album.albums.update_one(
        {"directory": path}, {"$setOnInsert": document}, upsert=True
    )
    if result.upserted_id:
        LOG.debug(f'Added album "{path}" as child of "{parent}"')
        return result.upserted_id
    else:
        result = async_client.ai_album.albums.find_one({"directory": path})
        return result['_id']


def record_media(name: str, path: str, album_id: Optional[str]) -> None:
    document = {
        "name": name,
        "path": path,
        "albumId": album_id,
    }
    result = async_client.ai_album.media.update_one(
        {"path": path}, {"$setOnInsert": document}, upsert=True
    )
    if result.upserted_id:
        LOG.debug(f'Added media "{name}" for album "{album_id}" from path "{path}"')



def init_path_graph():
    pg = nx.DiGraph()
    pg.add_node(DAG_ROOT, id=None, path="")
    return pg


def run_indexing(dir):
    LOG.debug("Start indexing files")
    LOG.debug(f"Traversing {dir}/data")
    pg = init_path_graph()

    for file in glob.iglob(f"{dir}/data/**", recursive=True):
        resource_path = file.replace(f"{dir}/data/", "")
        resource_path_parts = resource_path.split("/")

        path_parts = resource_path_parts[:-1]
        resource_name = resource_path_parts[-1]

        # files in /data
        if (
            len(path_parts) == 0
            and len(resource_name) != 0
            and pathlib.Path(file).is_file()
        ):
            record_media(resource_name, resource_path, None)

        # files nested within folders
        elif (
            len(path_parts) != 0
            and len(resource_name) != 0
            and pathlib.Path(file).is_file()
        ):
            if not pg.has_successor(DAG_ROOT, f"{DAG_ROOT}/{path_parts[0]}"):
                pg = init_path_graph()
                last_node = DAG_ROOT

                for itr_part in path_parts:
                    part = f"{last_node}/{itr_part}"
                    pg.add_node(part)
                    pg.add_edge(last_node, part)
                    pg.nodes[part][
                        "path"
                    ] = f'{pg.nodes[last_node]["path"]}/{itr_part}'.lstrip("/")
                    pg.nodes[part]["id"] = record_album(
                        pg.nodes[part]["path"], pg.nodes[last_node]["id"]
                    )
                    last_node = part

                record_media(resource_name, resource_path, pg.nodes[part]["id"])
            else:
                last_node = DAG_ROOT

                for part in path_parts:
                    part = f"{last_node}/{part}"

                    if pg.has_successor(last_node, part):
                        last_node = list(pg.neighbors(last_node))[0]
                        continue

                    # remove all the subsequent nodes
                    removables = list(nx.dfs_preorder_nodes(pg, last_node))[1:]
                    for r in removables:
                        pg.remove_node(r)

                    break

                last_node = DAG_ROOT

                for itr_part in path_parts:
                    part = f"{last_node}/{itr_part}"

                    if pg.has_successor(last_node, part):
                        last_node = list(pg.neighbors(last_node))[0]
                        continue

                    pg.add_node(part)
                    pg.add_edge(last_node, part)
                    pg.nodes[part][
                        "path"
                    ] = f'{pg.nodes[last_node]["path"]}/{itr_part}'.lstrip("/")
                    pg.nodes[part]["id"] = record_album(
                        pg.nodes[part]["path"], pg.nodes[last_node]["id"]
                    )

                record_media(resource_name, resource_path, pg.nodes[part]["id"])
    LOG.debug("Finish indexing files")
