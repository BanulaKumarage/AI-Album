conn = new Mongo({ useUnifiedTopology: true });
db = conn.getDB("ai_album");


db.createCollection('albums');
db.createCollection('media');
