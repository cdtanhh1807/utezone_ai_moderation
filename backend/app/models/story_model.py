from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


# ---------------------
# Pydantic helpers
# ---------------------
class PyObjectId(ObjectId):

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        json_schema = handler(schema)
        json_schema.update(type="string")
        return json_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


# ---------------------
# Sub-models
# ---------------------
class React(BaseModel):
    love: List[str] = Field(default_factory=list)
    like: List[str] = Field(default_factory=list)
    haha: List[str] = Field(default_factory=list)
    wow: List[str] = Field(default_factory=list)
    sad: List[str] = Field(default_factory=list)
    angry: List[str] = Field(default_factory=list)


class VideoTrim(BaseModel):
    startAt: float
    duration: float
    hasOriginalSound: bool = True



class TextLayer(BaseModel):
    id: Optional[str] = None
    text: str
    x: float
    y: float
    color: str = "#ffffff"
    fontSize: Optional[int] = None
    scale: Optional[float] = 1.0
    rotate: Optional[float] = 0.0
    font: Optional[str] = "Arial"
    align: Optional[str] = "center"
    background: Optional[str] = None


class Music(BaseModel):
    name: str
    fileid: str
    url: Optional[str] = None
    startAt: float = 0
    duration: float = 0
    
class Story(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    createdBy: str
    createdAt: datetime
    expiresAt: datetime

    mediaType: str                # image | video
    mediaUrls: List[str]
    thumbnails: List[str]

    textLayers: List[TextLayer] = Field(default_factory=list)
    music: Optional[Music] = None
    videoTrim: Optional[VideoTrim] = None
    react: React = Field(default_factory=React)
    viewedBy: List[str] = Field(default_factory=list)

    status: str = "active"

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}