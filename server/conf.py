from multiprocessing import cpu_count

# mongo_db_host = 'mongo'
mongo_db_host = "localhost"
mongo_db_port = 27017
mongo_db_user = "aialbumadmin"
mongo_db_password = "aialbumpw"
mongo_db_database = "ai_album"
mongo_db_auth = "admin"

# gpu/cpu configs
image_captioning_workers_per_gpu = 4
face_detection_workers_per_device = 1
face_detection_batch_size = 128
face_clustering_workers = cpu_count()
face_detector = "mtcnn"
face_model = "ArcFace"
face_distance_metric = "cosine"
face_distance_threshold = 0.8
face_count_prominance_threshold = 2

# album
thumbnail_resolution = 250, 250

# format support
supported_image_types = [
    "jpg",
    "JPG",
    "JPEG",
    "jpeg",
    "HEIC",
    "heic"
]

