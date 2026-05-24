from datetime import datetime, timedelta, timezone
from typing import List
from core.database import db
from bson import ObjectId


class ReportRepository:

    collection = db["report"]

    @staticmethod
    async def find_all() -> list[dict]:
        reports = []
        async for report in ReportRepository.collection.find():
            reports.append(report)
        return reports
    
    @staticmethod
    async def find_all_account_report() -> list[dict]:
        reports = []
        async for report in ReportRepository.collection.find({"typeContent": "account", "check": False}):
            reports.append(report)
        return reports
    
    @staticmethod
    async def find_all_post_report() -> list[dict]:
        reports = []
        async for report in ReportRepository.collection.find({"typeContent": "post", "check": False}):
            reports.append(report)
        return reports

    @staticmethod
    async def find_all_comment_report() -> list[dict]:
        reports = []
        async for report in ReportRepository.collection.find({"typeContent": "comment", "check": False}):
            reports.append(report)
        return reports
    
    @staticmethod
    async def find_all_message_report() -> list[dict]:
        reports = []
        async for report in ReportRepository.collection.find({"typeContent": "message", "check": False}):
            reports.append(report)
        return reports
    
    @staticmethod
    async def find_by_id(report_id: str) -> dict | None:
        return await ReportRepository.collection.find_one({"_id": ObjectId(report_id)})

    @staticmethod
    async def update(data: dict) -> dict | None:
        report_id = data.pop("id", None)
        if not report_id: return None
        await ReportRepository.collection.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": data}
        )
        return await ReportRepository.find_by_id(report_id)
    
    @staticmethod
    async def update_check_by_element(data: dict, approveBy: str, status: str):
        element = data.get("element")
        elementId = data.get("elementId")
        policyId = data.get("policyId")
        timestamp = datetime.now()

        if not element or not elementId or not policyId or not approveBy:
            return None

        if element == "account":
            filter_query = {
                "typeContent": "account",
                "violatorEmail": elementId,
                "policyId": policyId,
                "check": False
            }
        elif element != "account":
            filter_query = {
                "contentId": elementId,
                "policyId": policyId
            }
        else:
            return None

        update_query = {
            "$set": {"check": True, "approveBy": approveBy, "approveAt": timestamp, "status": status}
        }

        try:
            result = await ReportRepository.collection.update_many(filter_query, update_query)
            if result.matched_count == 0:
                return False
            return True
        except Exception:
            return False
        
    @staticmethod
    async def find_violator_email_by_content_id(content_id: str) -> str | None:
        document = await ReportRepository.collection.find_one({"contentId": content_id})
        if document:
            return document.get("violatorEmail")
        return None
    
    @staticmethod
    async def find_all_account_approve() -> list[dict]:
        reports = []
        query = {
            "typeContent": "account",
            "check": True,
            "approveBy": {"$exists": True}
        }
        async for report in ReportRepository.collection.find(query):
            reports.append(report)
        return reports
    
    @staticmethod
    async def find_all_post_approve() -> list[dict]:
        reports = []
        query = {
            "typeContent": "post",
            "check": True,
            "approveBy": {"$exists": True}
        }
        async for report in ReportRepository.collection.find(query):
            reports.append(report)
        return reports
    
    @staticmethod
    async def find_all_comment_approve() -> list[dict]:
        reports = []
        query = {
            "typeContent": "comment",
            "check": True,
            "approveBy": {"$exists": True}
        }
        async for report in ReportRepository.collection.find(query):
            reports.append(report)
        return reports

    @staticmethod
    async def find_all_message_approve() -> list[dict]:
        reports = []
        query = {
            "typeContent": "message",
            "check": True,
            "approveBy": {"$exists": True}
        }
        async for report in ReportRepository.collection.find(query):
            reports.append(report)
        return reports
    
    @staticmethod
    async def insert(data: dict) -> dict:
        result = await ReportRepository.collection.insert_one(data)
        new_report = await ReportRepository.collection.find_one({"_id": result.inserted_id})
        return new_report
    
    @staticmethod
    async def get_report_of_day() -> int:
        posts_today = await ReportRepository.collection.find({
            'check': False
        }).to_list(None) 
        return len(posts_today)
    
    @staticmethod
    async def get_reports_in_day(date: datetime) -> List[dict]:
        start_of_day = datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)

        reports = await ReportRepository.collection.find({
            "reportedAt": {
                "$gte": start_of_day,
                "$lt": end_of_day
            }
        }).to_list(length=None)

        result = []
        for r in reports:
            result.append({
                "typeContent": r.get("typeContent", None),
                "contentId": r.get("contentId", None),
                "content": r.get("content", None),
                "violatorEmail": r.get("violatorEmail", None),
                "contentParentId": r.get("contentParentId", None)
            })

        return result

        return reports
    
    @staticmethod
    async def find_report_by_annunciator(email: str) -> list[dict]:
        reports = []
        async for report in ReportRepository.collection.find({
            "annunciatorEmail": email
        }):
            reports.append(report)
        return reports
    
    @staticmethod
    async def find_report_with_violator(email: str) -> list[dict]:
        reports = []
        async for report in ReportRepository.collection.find({
            "violatorEmail": email
        }):
            reports.append(report)
        return reports



    

    