from collections import defaultdict
from datetime import datetime
from typing import List, Optional
from dto.account.request.update_account_request import UpdateAccountRequest
from dto.comment.request.update_status_comment_reply_request import UpdateStatusCommentReplyRequest
from dto.comment.response.update_status_comment_reply_response import UpdateStatusCommentReplyResponse
from dto.complaint.request.action_complaint_request import ActionComplaintRequest
from dto.complaint.request.add_complaint_request import AddComplaintRequest
from dto.complaint.request.get_all_complaint_request import GetAllComplaintRequest
from dto.complaint.response.action_complaint_response import ActionComplaintResponse
from dto.complaint.response.add_complaint_request import AddComplaintResponse
from dto.complaint.response.get_all_complaint_response import GetAllComplaintResponse
from dto.post.request.update_post_request import UpdatePostRequest
from dto.statistic.request.get_complaint_of_day_request import GetComplaintOfDayRequest
from dto.statistic.response.get_complaint_of_day_response import GetComplaintOfDayResponse
from models.announce_model import Announce
from models.ban_model import Ban
from models.complaint_model import Complaint
from models.violation_model import Violation
from repositories.announce_repository import AnnounceRepository
from repositories.ban_repository import BanRepository
from repositories.comment_repository import CommentRepository
from repositories.complaint_repository import ComplaintRepository
from repositories.policy_repository import PolicyRepository
from services.impls.account_service_impl import AccountServiceImpl
from services.impls.comment_service_impl import CommentServiceImpl
from services.impls.post_service_impl import PostServiceImpl
from services.interfaces.complaint_service_interface import IComplaintService
from repositories.account_repository import AccountRepository
from repositories.violation_repository import ViolationRepository
from models.account_model import Account, Permission
from models.policy_model import Policy
from models.base_model import bson_to_dict
from typing import List

from core.redis import delete_ban_countdown

class ComplaintServiceImpl(IComplaintService):

    async def get_policy(self, policyId: str) -> Policy:
        dic_policy = await PolicyRepository.find_by_id(policyId)
        return Policy(**bson_to_dict(dic_policy))
    
    async def get_user_infor(self, email: str) -> Account:
        dic_user = await AccountRepository.find_by_email(email)
        return Account(**bson_to_dict(dic_user))

    async def get_violation(self, violatorEmail: str, policyId: str) -> Violation | None:
        dic_violation = await ViolationRepository.find_by_violator_and_policy(violatorEmail, policyId)
        if dic_violation:
            return Violation(**bson_to_dict(dic_violation))
        return None

    async def get_all(self, complaint_list: GetAllComplaintRequest) -> Optional[List[GetAllComplaintResponse]]:
        dic_complaints = await ComplaintRepository.find_all()
        complaints = [Complaint(**bson_to_dict(complaint)) for complaint in dic_complaints]

        rs_list: List[GetAllComplaintResponse] = []
        for cp in complaints:
            policy = await self.get_policy(cp.policyId)
            complainant = await self.get_user_infor(cp.complainantEmail)
            contentId: Optional[str] = None
            contentParentId: Optional[str] = None
            content: Optional[str] = None
            #reply comment
            path: Optional[str] = None
            #reply comment
            if cp.contentId:
                contentId = cp.contentId
                if cp.contentParentId:
                    contentParentId = cp.contentParentId
                    content = cp.content

                    #reply comment
                    if cp.path:
                        path = cp.path
                    #reply comment

            rs = GetAllComplaintResponse(
                id=str(cp.id),
                policyId=cp.policyId,
                policyName=policy.name,
                action=policy.action.detail,
                complainantEmail=complainant.email,
                complainantName=complainant.userInfo.fullName,
                typeContent=cp.typeContent,
                contentId=contentId,
                contentParentId=contentParentId,
                #reply comment
                path=path,
                #reply comment
                content=content,
                description=cp.description,
                complaintAt=cp.complaintAt,
                approveBy=cp.approveBy,
                approveAt=cp.approveAt,
                verify=cp.verify
            )
            rs_list.append(rs)

        for rs_item in rs_list:
            vio = await self.get_violation(rs_item.complainantEmail, rs_item.policyId)
            if vio:
                dt: List[datetime] = []
                for time in vio.updatedAt:
                    dt.append(time.at)
                rs_item.violation = dt

        rs_list.sort(key=lambda x: x.complaintAt, reverse=True)
        return rs_list
    
    async def update(self, req: Complaint) -> Optional[Complaint]:
        updated_complaint = await ComplaintRepository.update(req.model_dump(exclude_none=True))
        if updated_complaint:
            return Complaint(**bson_to_dict(updated_complaint))
        return None

    async def reject(self, req: ActionComplaintRequest) -> Optional[ActionComplaintResponse]:
        dic_complaint = await ComplaintRepository.find_by_id(req.id)
        complaint: Complaint = Complaint(**bson_to_dict(dic_complaint))
        complaint.verify = False
        rs = await self.update(complaint)
        if rs:
            return ActionComplaintResponse(success=True, message="Ok")
        return ActionComplaintResponse(success=False, message="Error")

    async def approve(self, req: ActionComplaintRequest) -> Optional[ActionComplaintResponse]:
        dic_complaint = await ComplaintRepository.find_by_id(req.id)
        complaint: Complaint = Complaint(**bson_to_dict(dic_complaint))
        complaint.verify = True
        rs = await self.update(complaint)
        if rs:
            dic_violation = await ViolationRepository.find_and_remove_update_at(complaint.complainantEmail, complaint.policyId, complaint.approveAt)
            if dic_violation:
                violation: Violation = Violation(**bson_to_dict(dic_violation))
                dic_ban = await BanRepository.find_and_delete_ban(complaint.complainantEmail, str(violation.id), complaint.approveAt)
                if dic_ban:
                    ban: Ban = Ban(**bson_to_dict(dic_ban))
                    dic_account = await AccountRepository.find_by_email(ban.violatorEmail)
                    account: Account = Account(**bson_to_dict(dic_account))
                    pernum = account.permission.pernum
                    policy = await self.get_policy(violation.policyId)
                    pernum_policy = policy.action.permission

                    unban_pernum = ''.join(['1' if pernum[i] == pernum_policy[i] else '0' for i in range(len(pernum))])
                    account.permission.pernum = unban_pernum

                    account_service = AccountServiceImpl()
                    acc_update = await account_service.update(account_req=UpdateAccountRequest(id=str(account.id), permission=Permission(pernum=unban_pernum, validity=account.permission.validity)))

                    #unban_with_redis
                    for idx, action in enumerate(["post", "comment", "message"]):
                        if unban_pernum[idx] == '1' and pernum[idx] == '0':  # vừa được trả
                            await delete_ban_countdown(account.email, action)
                    #unban_with_redis
                if complaint.contentId:
                    polic: Policy = await self.get_policy(complaint.policyId)
                    if complaint.contentParentId:
                        #reply comment
                        if complaint.path:
                            cmt_service = CommentServiceImpl()
                            req_cmt = UpdateStatusCommentReplyRequest(postId=complaint.contentParentId, commentId=complaint.contentId, path=complaint.path, status="active")
                            cmt = await cmt_service.update_status_comment_reply(req=req_cmt)
                            if cmt:
                                #announce
                                contentAnnounce: str = "Đơn khiếu nại về bình luận: " + complaint.content + "... của bạn đã được phê duyệt"
                                announce = Announce(senderEmail="Hệ thống", receiverEmail=complaint.complainantEmail, type="complaint", contentAnnounce=contentAnnounce,
                                                    isRead=False, createdAt=datetime.now(), contentId=complaint.contentId,
                                                    contentParentId=complaint.contentParentId, content=complaint.content, policyName=polic.name, policyId=str(polic.id),
                                                    approveBy=req.actionBy, approveAt=datetime.now())
                                dic_announce_insert = await AnnounceRepository.insert(announce.model_dump())
                                #announce
                        #reply comment
                        else:
                            post_service = PostServiceImpl()
                            post = await post_service.update_comment_status(complaint.contentParentId, complaint.contentId, "active")
                            #announce
                            dic_comment_info = await CommentRepository.get_comment_info(post.post.id, complaint.contentId)
                            contentAnnounce: str = "Đơn khiếu nại về bình luận: " + complaint.content + "... của bạn đã được phê duyệt"
                            announce = Announce(senderEmail="Hệ thống", receiverEmail=complaint.complainantEmail, type="complaint", contentAnnounce=contentAnnounce,
                                                isRead=False, createdAt=datetime.now(), contentId=complaint.contentId,
                                                contentParentId=complaint.contentParentId, content=complaint.content, policyName=polic.name, policyId=str(polic.id),
                                                approveBy=req.actionBy, approveAt=datetime.now())
                            dic_announce_insert = await AnnounceRepository.insert(announce.model_dump())
                            #announce
                    else:
                        post_service = PostServiceImpl()
                        req = UpdatePostRequest(id=complaint.contentId, status="active")
                        post = await post_service.update(req)

                        #announce
                        contentAnnounce: str = ""
                        if post.post.title:
                            contentAnnounce = "Đơn khiếu nại bài viết: " + post.post.title + "... của bạn đã được phê duyệt"
                        else: contentAnnounce = "Đơn khiếu nại bài viết của bạn đã được phê duyệt"
                        announce = Announce(senderEmail="Hệ thống", receiverEmail=complaint.complainantEmail, type="complaint", contentAnnounce=contentAnnounce,
                                            isRead=False, createdAt=datetime.now(), contentId=complaint.contentId, policyName=polic.name, policyId=str(polic.id))
                        dic_announce_insert = await AnnounceRepository.insert(announce.model_dump())
                        #announce
                return ActionComplaintResponse(success=True, message="Ok")
        return ActionComplaintResponse(success=False, message="Error")
    
    async def add_complaint(self, req: AddComplaintRequest) -> Optional[AddComplaintResponse]:
        rs = await ComplaintRepository.insert(req.model_dump())
        if rs:
            return AddComplaintResponse(complaint=Complaint(**bson_to_dict(rs)))
        return None
    
    async def get_complaint_of_day(self, req: GetComplaintOfDayRequest) -> GetComplaintOfDayResponse:
        rs = await ComplaintRepository.get_complaint_of_day()
        return GetComplaintOfDayResponse(success=True, data=rs)

