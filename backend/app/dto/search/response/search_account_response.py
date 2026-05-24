from pydantic import BaseModel
from typing import List
from models.account_model import Account


class SearchAccountResponse(BaseModel):
    account_list: List[Account]


