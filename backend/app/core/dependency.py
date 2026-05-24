from services.impls.ai_service_impl import AIServiceImpl
from services.impls.announce_service_impl import AnnounceServiceImpl
from services.impls.ban_service_impl import BanServiceImpl
from services.impls.comment_service_impl import CommentServiceImpl
from services.impls.complaint_service_impl import ComplaintServiceImpl
from services.impls.incident_report_service_impl import IncidentReportServiceImpl
from services.impls.message_service_impl import MessageServiceImpl
from services.impls.policy_service_impl import PolicyServiceImpl
from services.impls.post_saved_service_impl import PostSavedServiceImpl
from services.impls.report_service_impl import ReportServiceImpl
from services.impls.search_service_impl import SearchServiceImpl
from services.impls.story_service_impl import StoryServiceImpl
from services.interfaces.ai_service_interface import IAIService
from services.interfaces.announce_service_interface import IAnnounceService
from services.interfaces.ban_service_interface import IBanService
from services.interfaces.comment_service_interface import ICommentService
from services.interfaces.complaint_service_interface import IComplaintService
from services.interfaces.incident_report_service_interface import IIncidentReportService
from services.interfaces.message_service_interface import IMessageService
from services.interfaces.policy_service_interface import IPolicyService
from services.interfaces.post_saved_service_interface import IPostSavedService
from services.interfaces.post_service_interface import IPostService
from services.impls.post_service_impl import PostServiceImpl
from services.interfaces.account_service_interface import IAccountService
from services.impls.account_service_impl import AccountServiceImpl
from services.interfaces.report_service_interface import IReportService
from services.interfaces.search_service_interface import ISearchService
from services.interfaces.story_service_interface import IStoryService

def get_post_service() -> IPostService:
    return PostServiceImpl()

def get_account_service() -> IAccountService:
    return AccountServiceImpl()

def get_policy_service() -> IPolicyService:
    return PolicyServiceImpl()

def get_report_service() -> IReportService:
    return ReportServiceImpl()

def get_ban_service() -> IBanService:
    return BanServiceImpl()

def get_complaint_service() -> IComplaintService:
    return ComplaintServiceImpl()

def get_search_service() -> ISearchService:
    return SearchServiceImpl()

def get_comment_service() -> ICommentService:
    return CommentServiceImpl()

def get_story_service() -> IStoryService:
    return StoryServiceImpl()

def get_message_service() -> IMessageService:
    return MessageServiceImpl()

def get_announce_service() -> IAnnounceService:
    return AnnounceServiceImpl()

def get_ai_service() -> IAIService:
    return AIServiceImpl()

def get_post_saved_service() -> IPostSavedService:
    return PostSavedServiceImpl()

def get_incident_report_service() -> IIncidentReportService:
    return IncidentReportServiceImpl()