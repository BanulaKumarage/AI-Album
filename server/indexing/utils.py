from threading import Lock

from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorCollection


class DataLoader:
    def __init__(
        self,
        collection: Collection | AsyncIOMotorCollection,
        query: dict,
        projection: dict,
        sort: str,
        batch_size: int = 100,
    ) -> None:
        self.lock = Lock()
        self.collection = collection
        self.query = query
        self.projection = projection
        self.sort = sort
        self.batch_size = batch_size
        self.cursor = self.collection.find(query, projection=projection).sort(sort)
        self.count = self.collection.count_documents(self.query)

    def get_next_batch(self) -> list:
        batch = []
        with self.lock:
            for item in self.cursor:
                batch.append(item)
                if len(batch) == self.batch_size:
                    break
        return batch

    def get_count(self):
        return self.count
