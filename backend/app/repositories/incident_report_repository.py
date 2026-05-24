from datetime import datetime
from typing import Optional
from core.database import db

class IncidentReportRepository:

    collection = db["incident_report"]

    @staticmethod
    async def find_all() -> list[dict]:
        list_dic = []
        async for dic in IncidentReportRepository.collection.find().sort("reportedAt", -1):
            list_dic.append(dic)
        return list_dic
    
    @staticmethod
    async def insert(data: dict) -> dict:
        result = await IncidentReportRepository.collection.insert_one(data)
        new_c = await IncidentReportRepository.collection.find_one({"_id": result.inserted_id})
        return new_c