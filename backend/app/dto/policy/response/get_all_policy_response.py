from pydantic import BaseModel
from typing import List
from models.policy_model import Policy


class GetAllPolicyResponse(BaseModel):
    policy_list: List[Policy]


