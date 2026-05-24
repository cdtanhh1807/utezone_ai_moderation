from pydantic import BaseModel
from models.account_model import Account


class RegisterUserResponse(BaseModel):
    account: Account