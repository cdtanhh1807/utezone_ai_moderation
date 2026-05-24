from fastapi import APIRouter, Depends, HTTPException
from dto.policy.request.add_policy_request import AddPolicyRequest
from dto.policy.request.get_all_action_request import GetAllActionRequest
from dto.policy.request.get_all_policy_content_request import GetAllPolicyContentRequest
from dto.policy.request.get_all_policy_request import GetAllPolicyRequest
from dto.policy.request.update_policy_request import UpdatePolicyRequest
from dto.policy.response.add_policy_response import AddPolicyResponse
from dto.policy.response.get_all_action_response import GetAllActionResponse
from dto.policy.response.get_all_policy_response import GetAllPolicyResponse
from dto.policy.response.update_policy_response import UpdatePolicyResponse
from services.interfaces.policy_service_interface import IPolicyService
from core.dependency import get_policy_service
from utils.security import get_current_user


router = APIRouter()

@router.get("/get_all_policy", response_model=GetAllPolicyResponse)
async def list_policys(
    current_user: dict = Depends(get_current_user),
    service: IPolicyService = Depends(get_policy_service)
):
    # if (current_user["role"] != "Administrator"):
    #     raise HTTPException(status_code=403, detail="Failed!")
    policy_list = GetAllPolicyRequest()
    return await service.get_all(policy_list)

@router.get("/get_all_action", response_model=GetAllActionResponse)
async def list_actions(
    current_user: dict = Depends(get_current_user),
    service: IPolicyService = Depends(get_policy_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    action_list = GetAllActionRequest()
    return await service.get_all_action(action_list)

@router.put("/update_policy/{policy_id}", response_model=UpdatePolicyResponse)
async def update_policy(
    policy_id: str,
    policy: UpdatePolicyRequest,
    current_user: dict = Depends(get_current_user),
    service: IPolicyService = Depends(get_policy_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    policy.id = policy_id
    updated = await service.update(policy)
    if not updated:
        raise HTTPException(status_code=404, detail="Policy not found")
    return updated

@router.put("/unset_action/{policy_id}", response_model=UpdatePolicyResponse)
async def unset_action(
    policy_id: str,
    policy: UpdatePolicyRequest,
    current_user: dict = Depends(get_current_user),
    service: IPolicyService = Depends(get_policy_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    policy.id = policy_id
    updated = await service.unset_action(policy)
    if not updated:
        raise HTTPException(status_code=404, detail="Policy not found")
    return updated

@router.post("/add_policy", response_model=AddPolicyResponse)
async def add_post(
    policy: AddPolicyRequest,
    current_user: dict = Depends(get_current_user),
    service: IPolicyService = Depends(get_policy_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    return await service.add(policy)

# @router.get("/get_all_policy_content", response_model=GetAllPolicyResponse)
# async def list_policys(
#     # current_user: dict = Depends(get_current_user),
#     policy_list: GetAllPolicyContentRequest,
#     service: IPolicyService = Depends(get_policy_service)
# ):
#     return await service.get_all_with_content(policy_list)

@router.post("/get_all_policy_content", response_model=GetAllPolicyResponse)
async def list_policys(
    policy_list: GetAllPolicyContentRequest,
    service: IPolicyService = Depends(get_policy_service)
):
    return await service.get_all_with_content(policy_list)