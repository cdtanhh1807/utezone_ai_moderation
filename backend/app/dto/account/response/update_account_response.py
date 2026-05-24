from models.account_model import Account
from pydantic import BaseModel


class UpdateAccountResponse(BaseModel):
    account: Account