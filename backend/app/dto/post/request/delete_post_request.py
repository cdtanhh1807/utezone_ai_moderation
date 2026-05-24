from pydantic import BaseModel


class DeletePostRequest(BaseModel):
    id: str
