from abc import ABC, abstractmethod
from typing import List, Optional

from dto.report.request.approve_report_request import ApproveReportRequest
from dto.report.request.get_all_history_approve_request import GetAllHistoryApproveRequest
from dto.report.request.get_all_report_request import GetAllReportRequest
from dto.report.request.get_my_report_request import GetMyReportRequest
from dto.report.request.get_report_me_request import GetReportMeRequest
from dto.report.request.reject_report_request import RejectReportRequest
from dto.report.request.send_report_request import SendReportRequest
from dto.report.request.update_report_request import UpdateReportRequest
from dto.report.response.approve_report_response import ApproveReportResponse
from dto.report.response.get_all_history_approve_reponse import GetAllHistoryApproveResponse
from dto.report.response.get_all_report_response import GetAllReportResponse
from dto.report.response.get_my_report_response import GetMyReportResponse
from dto.report.response.get_report_me_response import GetReportMeResponse
from dto.report.response.reject_report_response import RejectReportResponse
from dto.report.response.send_report_response import SendReportResponse
from dto.report.response.update_report_response import UpdateReportResponse
from dto.statistic.request.get_report_of_day_request import GetReportOfDayRequest
from dto.statistic.request.get_top_report_request import GetTopReportRequest
from dto.statistic.response.get_report_of_day_response import GetReportOfDayResponse
from dto.statistic.response.get_top_report_response import GetTopReportReponse


class IReportService(ABC):

    @abstractmethod
    async def get_all(self, report_list: GetAllReportRequest) -> Optional[List[GetAllReportResponse]]:
        pass

    @abstractmethod
    async def reject(self, report_req: RejectReportRequest) -> Optional[RejectReportResponse]:
        pass

    @abstractmethod
    async def approve(self, report_req: ApproveReportRequest) -> Optional[ApproveReportResponse]:
        pass

    @abstractmethod
    async def get_all_history_approve(self, report_req: GetAllHistoryApproveRequest) -> Optional[GetAllHistoryApproveResponse]:
        pass
    
    @abstractmethod
    async def send_report(self, req: SendReportRequest) -> Optional[SendReportResponse]:
        pass

    @abstractmethod
    async def get_report_of_day(self, req: GetReportOfDayRequest) -> GetReportOfDayResponse:
        pass

    @abstractmethod
    async def get_top_report(self, req: GetTopReportRequest) -> GetTopReportReponse:
        pass

    @abstractmethod
    async def get_my_report(self, req: GetMyReportRequest) -> List[GetMyReportResponse]:
        pass

    @abstractmethod
    async def get_report_me(self, req: GetReportMeRequest) -> List[GetReportMeResponse]:
        pass
