from models.policy_model import Policy
from pydantic import BaseModel


class UpdatePolicyResponse(BaseModel):
    policy: Policy