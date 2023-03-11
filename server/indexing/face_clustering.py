import logging
import gc
from threading import Event
import os
import shutil
import orjson
import glob
import pathlib

from deepface.DeepFace import dst
import dask_mongo
from dask.distributed import Client, LocalCluster

from server.db import async_client
from server.conf import (
    face_clustering_workers,
    mongo_db_database,
    mongo_db_host,
    mongo_db_port,
    mongo_db_user,
    mongo_db_password,
)


LOG = logging.getLogger(__name__)


def has_faces(document):
    if "faceEncodings" in document and len(document["faceEncodings"]) > 0:
        return True

    return False


def to_faces(document):
    array = []

    for fid, enc in enumerate(document["faceEncodings"]):
        dct = dict()
        dct["_id"] = str(document["_id"])
        dct["face"] = document["faces"][fid]
        dct["enc"] = enc
        dct["path"] = document["path"]
        array.append(dct)

    return array


def get_matching(this, that):
    dist = dst.findCosineDistance(this["enc"], that["enc"])
    if dist > 0.3:
        return None
    return this


def get_mismatching(this, that):
    dist = dst.findCosineDistance(this["enc"], that["enc"])
    if dist <= 0.3:
        return None
    return this


def record_face_group(group, path, face, count):
    async_client.ai_album.face_groups.insert_one(
        {"group": group, "path": path, "face": face, "facesCount": count}
    )


def record_group_face(group, path, face, is_prominant):
    async_client.ai_album.group_faces.insert_one(
        {"group": group, "path": path, "face": face, "isProminant": is_prominant}
    )


def record_group(task_dir, sub_dir, is_prominant):
    data_path = f"{task_dir}/face_groups/{sub_dir}"

    for group in glob.iglob(f"{data_path}/*"):
        group = pathlib.Path(group)
        resource_path = group.relative_to(data_path)
        (face_group,) = resource_path.parts
        count = 0
        entry = None

        for file in glob.iglob(f"{data_path}/{face_group}/*"):
            with open(file) as file:
                for line in file:
                    count += 1
                    line_entry = orjson.loads(line)
                    record_group_face(
                        face_group, line_entry["path"], line_entry["face"], is_prominant
                    )
                    if entry is None:
                        entry = line_entry

        record_face_group(face_group, entry["path"], entry["face"], count)


def run_face_clustering(task_dir, killer: Event):
    cluster = LocalCluster(n_workers=face_clustering_workers, threads_per_worker=1)
    client = Client(cluster)

    all_documents = dask_mongo.read_mongo(
        database=mongo_db_database,
        collection="media",
        connection_kwargs={
            "host": mongo_db_host,
            "port": mongo_db_port,
            "username": mongo_db_user,
            "password": mongo_db_password,
        },
        chunksize=100,
    )

    with_faces = all_documents.filter(has_faces)
    formatted = with_faces.map(to_faces)
    flattened = formatted.flatten()
    flattened = flattened.repartition(npartitions=face_clustering_workers)
    flattened = flattened.persist()

    source = flattened
    group_id_prominant = 1
    group_id_non_prominant = 1

    if os.path.isdir(f"{task_dir}/face_groups"):
        shutil.rmtree(f"{task_dir}/face_groups")

    LOG.debug("FACE-CLUSTERING: starting")
    LOG.debug(f"FACE-CLUSTERING: {cluster.dashboard_link}")

    while source.count().compute() > 0 and not killer.is_set():
        items = source.take(1, npartitions=source.npartitions)
        item = items[0]

        matching = source.map(get_matching, item)
        matching = matching.filter(lambda x: x is not None)
        matches = matching.count().compute()

        mismatching = source.map(get_mismatching, item)
        mismatching = mismatching.filter(lambda x: x is not None)
        matching = matching.map(orjson.dumps)

        if matches > 50:
            matching.to_textfiles(
                f"{task_dir}/face_groups/prominant/{group_id_prominant}"
            )
            group_id_prominant += 1
        else:
            matching.to_textfiles(
                f"{task_dir}/face_groups/non-prominant/{group_id_non_prominant}"
            )
            group_id_non_prominant += 1

        source = mismatching.repartition(npartitions=face_clustering_workers)
        source = source.persist()

    client.close()
    cluster.close()
    gc.collect()

    async_client.ai_album.face_groups.delete_many({})
    async_client.ai_album.group_faces.delete_many({})

    record_group(task_dir, "prominant", True)
    record_group(task_dir, "non-prominant", False)

    LOG.debug("FACE-CLUSTERING: completed")
