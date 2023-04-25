from server.db import async_client


async_client.ai_album.drop_collection("albums")
async_client.ai_album.drop_collection("media")
async_client.ai_album.drop_collection("faces")
async_client.ai_album.drop_collection("face_groups")
async_client.ai_album.media.update_many(
    {},
    {"$unset": {"caption": "", "faces": "", "faceEncodings": "", "probs": ""}},
)