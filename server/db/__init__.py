from pymongo import MongoClient
import motor.motor_asyncio

from server import conf


async_client = MongoClient(conf.mongo_db_host,
                     port=conf.mongo_db_port,
                     username=conf.mongo_db_user,
                     password=conf.mongo_db_password,
                     authSource=conf.mongo_db_auth)

client = motor.motor_asyncio.AsyncIOMotorClient(conf.mongo_db_host,
                     port=conf.mongo_db_port,
                     username=conf.mongo_db_user,
                     password=conf.mongo_db_password,
                     authSource=conf.mongo_db_auth)
