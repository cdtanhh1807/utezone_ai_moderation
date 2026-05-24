from typing import Optional
from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetJsonSchemaHandler

class PyObjectId(ObjectId):

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler: GetJsonSchemaHandler):
        json_schema = handler(schema)
        json_schema.update(type='string')
        return json_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)


# def bson_to_dict(doc: dict):
#     if "_id" in doc:
#         doc["_id"] = str(doc["_id"])
#     return doc


def bson_to_dict(doc: Optional[dict]) -> Optional[dict]:
    if doc is None:
        return None
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc