from pymongo import MongoClient

from server import conf


client = MongoClient(conf.mongo_db_host,
                     port=conf.mongo_db_port,
                     username=conf.mongo_db_user,
                     password=conf.mongo_db_password,
                     authSource=conf.mongo_db_auth)
