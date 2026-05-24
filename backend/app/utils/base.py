# utils/base.py
from bson import ObjectId

def bson_to_dict(document: dict) -> dict:
    """
    Chuyển _id ObjectId sang string, dùng khi trả về JSON.
    """
    if not document:
        return {}
    doc = document.copy()
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc
