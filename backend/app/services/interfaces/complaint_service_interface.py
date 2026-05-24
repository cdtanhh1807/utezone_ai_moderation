from abc import ABC, abstractmethod
from typing import List, Optional

from dto.complaint.request.action_complaint_request import ActionComplaintRequest
from dto.complaint.request.add_complaint_request import AddComplaintRequest
from dto.complaint.request.get_all_complaint_request import GetAllComplaintRequest
from dto.complaint.response.action_complaint_response import ActionComplaintResponse
from dto.complaint.response.add_complaint_request import AddComplaintResponse
from dto.complaint.response.get_all_complaint_response import GetAllComplaintResponse
from dto.statistic.request.get_complaint_of_day_request import GetComplaintOfDayRequest
from dto.statistic.response.get_complaint_of_day_response import GetComplaintOfDayResponse


class IComplaintService(ABC):

    @abstractmethod
    async def get_all(self, complaint_list: GetAllComplaintRequest) -> Optional[List[GetAllComplaintResponse]]:
        pass

    @abstractmethod
    async def reject(self, req: ActionComplaintRequest) -> Optional[ActionComplaintResponse]:
        pass

    @abstractmethod
    async def approve(self, req: ActionComplaintRequest) -> Optional[ActionComplaintResponse]:
        pass

    @abstractmethod
    async def add_complaint(self, req: AddComplaintRequest) -> Optional[AddComplaintResponse]:
        pass

    @abstractmethod
    async def get_complaint_of_day(self, req: GetComplaintOfDayRequest) -> GetComplaintOfDayResponse:
        pass