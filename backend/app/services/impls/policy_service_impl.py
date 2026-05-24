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
from models.policy_model import Action, Policy
from repositories.policy_repository import PolicyRepository
from services.interfaces.policy_service_interface import IPolicyService
from models.base_model import bson_to_dict


class PolicyServiceImpl(IPolicyService):
    
    async def get_all(self, policy_list: GetAllPolicyRequest) -> Optional[GetAllPolicyResponse]:
        policies = await PolicyRepository.find_all()
        return GetAllPolicyResponse(policy_list=[Policy(**bson_to_dict(policy)) for policy in policies]) 
    
    async def get_all_action(self, action_list: GetAllActionRequest) -> Optional[GetAllActionResponse]:
        actions = await PolicyRepository.find_all_action()
        return GetAllActionResponse( action_list=[Action(**bson_to_dict(action["action"])) for action in actions] )
    
    async def update(self, policy_req: UpdatePolicyRequest) -> Optional[UpdatePolicyResponse]:
        updated_policy = await PolicyRepository.update(policy_req.model_dump(exclude_none=True))
        if updated_policy:
            return UpdatePolicyResponse(policy=Policy(**bson_to_dict(updated_policy)))
        return None
    
    async def unset_action(self, policy_req: UpdatePolicyRequest) -> Optional[UpdatePolicyResponse]:
        updated_policy = await PolicyRepository.unset_action(policy_req.model_dump(exclude_none=True))
        if updated_policy:
            return UpdatePolicyResponse(policy=Policy(**bson_to_dict(updated_policy)))
        return None
    
    async def add(self, policy_req: AddPolicyRequest) -> Optional[AddPolicyResponse]:
        new_policy = await PolicyRepository.insert(policy_req.model_dump(exclude_none=True))
        if new_policy:
            return AddPolicyResponse(success=True, message="Completed")
        else:
            return AddPolicyResponse(success=False, message="Failed to add policy")
        
    async def get_all_with_content(self, policy_list: GetAllPolicyContentRequest) -> GetAllPolicyResponse:
        policies = await PolicyRepository.get_all_with_content(policy_list.content)
        return GetAllPolicyResponse(policy_list=[Policy(**bson_to_dict(policy)) for policy in policies]) 