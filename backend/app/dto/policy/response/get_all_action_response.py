from pydantic import BaseModel
from typing import List
from models.policy_model import Action


class GetAllActionResponse(BaseModel):
    action_list: List[Action]


