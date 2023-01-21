# import logging

# from pymongo.collection import Collection
# from pymongo.cursor import Cursor
# from pymongo.results import InsertOneResult


# LOG = logging.getLogger(__name__)


# def get_documents(collection: Collection, query: dict, skip: int, limit: int) -> Cursor:
#     LOG.debug(f'QUERY - {query}')
#     LOG.debug(f'COLLECTION - {collection.name}')
#     return []


# def save_document(collection: Collection, document: dict) -> InsertOneResult:
#     LOG.debug(f'DOCUMENT - {document}')
#     LOG.debug(f'COLLECTION - {collection.name}')

#     return collection.insert_one(document)
