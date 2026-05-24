from typing import List, Optional
from dto.ban.request.get_all_ban_request import GetAllBanRequest
from dto.ban.response.get_all_ban_response import GetAllBanResponse, BanDetail
from models.ban_model import Ban
from models.policy_model import Policy
from models.violation_model import Violation
from repositories.ban_repository import BanRepository 
from repositories.policy_repository import PolicyRepository
from repositories.violation_repository import ViolationRepository
from services.interfaces.ban_service_interface import IBanService 
from services.impls.account_service_impl import AccountServiceImpl
from models.base_model import bson_to_dict



class BanServiceImpl(IBanService):
    
    async def get_policy(self, policyId: str) -> Policy:
        dic_policy = await PolicyRepository.find_by_id(policyId)
        return Policy(**bson_to_dict(dic_policy))

    async def get_all(self, ban_list: GetAllBanRequest) -> Optional[List[GetAllBanResponse]]:
        dic_bans = await BanRepository.find_all()
        bans = [Ban(**bson_to_dict(ban)) for ban in dic_bans]
        rs: List[GetAllBanResponse] = []
        for item in bans:
            rs_item = GetAllBanResponse(id=str(item.id), violatorEmail=item.violatorEmail)
            account_service = AccountServiceImpl()
            violatorRole = await account_service.get_role_by_email(item.violatorEmail)
            rs_item.violatorRole = violatorRole
            rs_item_detail: List[BanDetail] = []
            for vio in item.violations:
                dic_item_violation = await ViolationRepository.find_by_id(vio.violationId)
                item_violation = Violation(**bson_to_dict(dic_item_violation))

                item_vio_policy_infor = await self.get_policy(item_violation.policyId)
                rs_item_ban_detail = BanDetail(policyName=item_vio_policy_infor.name, action=item_vio_policy_infor.action.detail, beginAt=vio.beginAt, endAt=vio.endAt)
                rs_item_detail.append(rs_item_ban_detail)
            
            rs_item.detail = rs_item_detail
            rs.append(rs_item)

        return rs
            


    