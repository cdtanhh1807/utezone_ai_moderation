from abc import ABC, abstractmethod
from typing import Optional

from dto.policy.request.add_policy_request import AddPolicyRequest
from dto.policy.request.get_all_action_request import GetAllActionRequest
from dto.policy.request.get_all_policy_content_request import GetAllPolicyContentRequest
from dto.policy.request.get_all_policy_request import GetAllPolicyRequest
from dto.policy.request.update_policy_request import UpdatePolicyRequest
from dto.policy.response.add_policy_response import AddPolicyResponse
from dto.policy.response.get_all_action_response import GetAllActionResponse
from dto.policy.response.get_all_policy_response import GetAllPolicyResponse
from dto.policy.response.update_policy_response import UpdatePolicyResponse


class IPolicyService(ABC):
    
    @abstractmethod
    async def get_all(self, policy_list: GetAllPolicyRequest) -> GetAllPolicyResponse:
        pass

    @abstractmethod
    async def get_all_action(self, action_list: GetAllActionRequest) -> GetAllActionResponse:
        pass

    @abstractmethod
    async def update(self, policy_req: UpdatePolicyRequest) -> Optional[UpdatePolicyResponse]:
        pass

    @abstractmethod
    async def unset_action(self, policy_req: UpdatePolicyRequest) -> Optional[UpdatePolicyResponse]:
        pass

    @abstractmethod
    async def add(self, policy_req: AddPolicyRequest) -> AddPolicyResponse:
        pass

    @abstractmethod
    async def get_all_with_content(self, policy_list: GetAllPolicyContentRequest) -> GetAllPolicyResponse:
        pass