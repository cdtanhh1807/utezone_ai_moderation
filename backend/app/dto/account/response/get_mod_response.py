from pydantic import BaseModel
from typing import List
from models.account_model import Account


class GetModResponse(BaseModel):
    account_list: List[Account]


