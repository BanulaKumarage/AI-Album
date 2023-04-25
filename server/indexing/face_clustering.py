import logging
import gc
from threading import Event
import os
import shutil
from bson import ObjectId
import orjson
import glob
import pathlib
from scipy.spatial import distance

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
    face_distance_metric,
    face_distance_threshold,
    face_model,
    face_count_prominance_threshold,
)


LOG = logging.getLogger(__name__)
FACE_MODEL = face_model
FACE_DISTANCE_METRIC = face_distance_metric
FACE_DISTANCE_THRESHOLD = face_distance_threshold


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


def get_matching(this, that, metric, threshold):
    if metric == "cosine":
        dist = distance.cosine(this["enc"], that["enc"])
    elif metric == "euclidean":
        dist = distance.euclidean(this["enc"], that["enc"])

    if dist > threshold:
        return None
    return this


def get_mismatching(this, that, metric, threshold):
    if metric == "cosine":
        dist = distance.cosine(this["enc"], that["enc"])
    elif metric == "euclidean":
        dist = distance.euclidean(this["enc"], that["enc"])

    if dist <= threshold:
        return None
    return this


def record_face_group(image_id, path, face, is_prominant):
    result = async_client.ai_album.face_groups.insert_one(
        {
            "imageId": ObjectId(image_id),
            "path": path,
            "face": face,
            "isProminant": is_prominant,
        }
    )
    return result.inserted_id


def update_face_group(id, count):
    async_client.ai_album.face_groups.update_one(
        {"_id": id},
        {
            "$set": {
                "facesCount": count,
            }
        },
    )


def record_face(image_id, group_id, path, face, is_prominant):
    async_client.ai_album.faces.insert_one(
        {
            "imageId": ObjectId(image_id),
            "groupId": group_id,
            "path": path,
            "face": face,
            "isProminant": is_prominant,
        }
    )


def save_to_db(task_dir, sub_dir, is_prominant):
    data_path = f"{task_dir}/face_groups/{sub_dir}"

    for group in glob.iglob(f"{data_path}/*"):
        group = pathlib.Path(group)
        resource_path = group.relative_to(data_path)
        (face_group,) = resource_path.parts
        count = 0
        group_id = None

        for file in glob.iglob(f"{data_path}/{face_group}/*"):
            with open(file) as fp:
                for line in fp:
                    count += 1
                    line_entry = orjson.loads(line)

                    if group_id is None:
                        group_id = record_face_group(
                            line_entry["_id"],
                            line_entry["path"],
                            line_entry["face"],
                            is_prominant,
                        )

                    record_face(
                        line_entry["_id"],
                        group_id,
                        line_entry["path"],
                        line_entry["face"],
                        is_prominant,
                    )
        update_face_group(group_id, count)


def run_face_clustering(task_dir, killer: Event):
    async_client.ai_album.face_groups.delete_many({})
    async_client.ai_album.faces.delete_many({})

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

        matching = source.map(
            get_matching, item, FACE_DISTANCE_METRIC, FACE_DISTANCE_THRESHOLD
        )
        matching = matching.filter(lambda x: x is not None)
        matches = matching.count().compute()

        mismatching = source.map(
            get_mismatching, item, FACE_DISTANCE_METRIC, FACE_DISTANCE_THRESHOLD
        )
        mismatching = mismatching.filter(lambda x: x is not None)
        matching = matching.map(orjson.dumps)

        if matches > face_count_prominance_threshold:
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

    save_to_db(task_dir, "prominant", True)
    save_to_db(task_dir, "non-prominant", False)

    LOG.debug("FACE-CLUSTERING: completed")
