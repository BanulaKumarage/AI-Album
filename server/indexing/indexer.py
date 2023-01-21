import hashlib
import os
import pathlib
import traceback
import logging
import glob
from typing import Optional

import networkx as nx

from server.db import albums, media


LOG = logging.getLogger(__name__)
DAG_ROOT = 'R'


# docs - https://stackoverflow.com/questions/24937495/how-can-i-calculate-a-hash-for-a-filesystem-directory-using-python
def GetHashofDirs(directory, verbose=0):
    import hashlib, os
    SHAhash = hashlib.md5()
    if not os.path.exists (directory):
        return -1

    try:
        for root, dirs, files in os.walk(directory):
            for names in files:
                filepath = os.path.join(root,names)
                
                try:
                    f1 = open(filepath, 'rb')
                except:
                    # You can't open the file for some reason
                    f1.close()
                    continue

                while 1:
                    # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf : break
                    SHAhash.update(hashlib.md5(buf).hexdigest())
                f1.close()

    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2

    return SHAhash.hexdigest()


def record_album(name: str, parent: Optional[str]):
    LOG.debug(f'Recording album "{name}" as child of "{parent}"')
    result = albums.create_album(name, name, parent)
    return result.inserted_id


def record_media(name: str, path: str, album_id: Optional[str]):
    LOG.debug(f'Recording media "{name}" for album "{album_id}" from path "{path}"')
    result = media.create_media(name, path, album_id)
    return result.inserted_id


def init_path_graph():
    pg =  nx.DiGraph()
    pg.add_node(DAG_ROOT, id=None)
    return pg


async def run_indexing(dir):
    LOG.debug(f'Traversing {dir}/data')
    pg =  init_path_graph()

    for file in glob.iglob(f'{dir}/data/**', recursive=True):
        resource_path = file.replace(f'{dir}/data/', '')
        resource_path_parts = resource_path.split('/')

        path_parts = resource_path_parts[:-1]
        resource_name = resource_path_parts[-1]

        # files in /data
        if len(path_parts) == 0 and len(resource_name) != 0 and pathlib.Path(file).is_file():
            record_media(resource_name, resource_path, None)

        # files nested within folders
        elif len(path_parts) != 0 and len(resource_name) != 0 and pathlib.Path(file).is_file():
            if not pg.has_successor(DAG_ROOT, f'{DAG_ROOT}/{path_parts[0]}'):
                pg = init_path_graph()                
                last_node = DAG_ROOT

                for part in path_parts:
                    part = f'{last_node}/{part}'
                    pg.add_node(part)
                    pg.add_edge(last_node, part)
                    pg.nodes[part]['id'] = record_album(part, pg.nodes[last_node]['id'])
                    last_node = part

                record_media(resource_name, resource_path, pg.nodes[part]['id'])
            else:
                last_node = DAG_ROOT

                for part in path_parts:
                    part = f'{last_node}/{part}'

                    if pg.has_successor(last_node, part):
                        last_node = list(pg.neighbors(last_node))[0]
                        continue

                    # remove all the subsequent nodes
                    removables = list(nx.dfs_preorder_nodes(pg, last_node))[1:]
                    for r in removables:
                        pg.remove_node(r)
                    
                    break
                
                last_node = DAG_ROOT

                for part in path_parts:
                    part = f'{last_node}/{part}'
                    
                    if pg.has_successor(last_node, part):
                        last_node = list(pg.neighbors(last_node))[0]
                        continue
                    
                    pg.add_node(part)
                    pg.add_edge(last_node, part)                
                    pg.nodes[part]['id'] = record_album(part, pg.nodes[last_node]['id'])

                record_media(resource_name, resource_path, pg.nodes[part]['id'])
