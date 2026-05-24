from bson import ObjectId
from core.database import db
from typing import List, Optional
from rapidfuzz import fuzz
import re

class AccountRepository:

    collection = db["account"]

    @staticmethod
    async def find_by_email(email: str) -> Optional[dict]:
        doc = await AccountRepository.collection.find_one({"email": email})
        if doc: return doc
        return None
    
    @staticmethod
    async def find_by_email_user(email: str, myAccount: dict) -> Optional[dict]:
        my_email = myAccount.get("email")
        my_blocks = myAccount["userInfo"].get("blocks", [])

        # Query account theo email
        doc = await AccountRepository.collection.find_one({"email": email})

        if not doc:
            return None

        # 1. Kiểm tra nếu bạn đã block account này → loại bỏ
        if email in my_blocks:
            return None

        # 2. Kiểm tra nếu account này đã block bạn → loại bỏ
        author_blocks = doc["userInfo"].get("blocks", [])
        if my_email in author_blocks:
            return None

        return doc

    
    @staticmethod
    async def insert(account: dict) -> Optional[dict]:
        rs = await AccountRepository.collection.insert_one(account)
        new_rs = await AccountRepository.collection.find_one({"_id": rs.inserted_id})
        return new_rs
    
    @staticmethod
    async def change_password(email: str, new_password: str) -> Optional[dict]:
        result = await AccountRepository.collection.update_one(
            {"email": email},
            {"$set": {"password": new_password}}
        )
        
        if result.modified_count == 0:
            return None

        updated_account = await AccountRepository.collection.find_one({"email": email})
        return updated_account
    
    @staticmethod
    async def find_all() -> list[dict]:
        accounts = []
        async for account in AccountRepository.collection.find({"hidden": {"$exists": False}}):
            accounts.append(account)
        return accounts
    
    @staticmethod
    async def find_by_id(account_id: str) -> dict | None:
        return await AccountRepository.collection.find_one({"_id": ObjectId(account_id)})

    @staticmethod
    async def update(data: dict) -> dict | None:
        account_id = data.pop("id", None)
        if not account_id: return None
        await AccountRepository.collection.update_one(
            {"_id": ObjectId(account_id)},
            {"$set": data}
        )
        return await AccountRepository.find_by_id(account_id)
    
    # @staticmethod
    # async def find_by_fullname(keySearch: str, myAccount: dict) -> Optional[list[dict]]:
    #     from rapidfuzz import fuzz

    #     my_email = myAccount.get("email")
    #     my_blocks = myAccount["userInfo"].get("blocks", [])

    #     # 1. Tách keySearch thành các từ
    #     parts = keySearch.lower().split()

    #     # 2. Tạo regex sơ bộ
    #     regex_conditions = [
    #         {
    #             "userInfo.fullName": {
    #                 "$regex": part[:2],
    #                 "$options": "i"
    #             }
    #         }
    #         for part in parts if len(part) >= 2
    #     ]

    #     if not regex_conditions:
    #         regex_conditions = [{"userInfo.fullName": {"$regex": ".*"}}]

    #     # 3. Query sơ bộ: loại bỏ account bị block bởi bạn
    #     cursor = AccountRepository.collection.find({
    #         "$or": regex_conditions,
    #         "email": {"$nin": my_blocks}   # bạn đã block
    #     })

    #     candidates = await cursor.to_list(length=None)

    #     if not candidates:
    #         return None

    #     # 4. Fuzzy filter + kiểm tra mutual block (tài khoản được tìm không block bạn)
    #     results = []
    #     for acc in candidates:
    #         # Check mutual block
    #         acc_blocks = acc["userInfo"].get("blocks", [])
    #         if myAccount.get("email") in acc_blocks:
    #             continue  # account này đã block bạn, loại bỏ

    #         # Fuzzy match
    #         full_name = acc["userInfo"]["fullName"]
    #         score = fuzz.token_sort_ratio(full_name.lower(), keySearch.lower())
    #         if score >= 50:
    #             results.append(acc)

    #     return results if results else None
    @staticmethod
    async def find_by_fullname(keySearch: str, myAccount: dict) -> Optional[List[dict]]:
        from rapidfuzz import fuzz

        my_email = myAccount.get("email")
        my_blocks = myAccount["userInfo"].get("blocks", [])

        # =========================
        # 0. CHECK KEYSEARCH LÀ EMAIL
        # =========================
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(email_pattern, keySearch):
            acc = await AccountRepository.find_by_email(keySearch)

            if not acc:
                return None

            # ❌ bạn đã block họ
            if acc["email"] in my_blocks:
                return None

            # ❌ họ đã block bạn
            acc_blocks = acc["userInfo"].get("blocks", [])
            if my_email in acc_blocks:
                return None

            # ✅ hợp lệ → return luôn
            return [acc]

        # =========================
        # 1. FLOW CŨ (SEARCH NAME)
        # =========================
        parts = keySearch.lower().split()

        regex_conditions = [
            {
                "userInfo.fullName": {
                    "$regex": part[:2],
                    "$options": "i"
                }
            }
            for part in parts if len(part) >= 2
        ]

        if not regex_conditions:
            regex_conditions = [{"userInfo.fullName": {"$regex": ".*"}}]

        cursor = AccountRepository.collection.find({
            "$or": regex_conditions,
            "email": {"$nin": my_blocks}
        })

        candidates = await cursor.to_list(length=None)

        if not candidates:
            return None

        results = []
        for acc in candidates:
            acc_blocks = acc["userInfo"].get("blocks", [])

            # ❌ mutual block
            if my_email in acc_blocks:
                continue

            full_name = acc["userInfo"]["fullName"]
            score = fuzz.token_sort_ratio(full_name.lower(), keySearch.lower())

            if score >= 50:
                results.append(acc)

        return results if results else None


    
    @staticmethod
    async def find_by_department(department: str, myAccount: dict) -> Optional[list[dict]]:
        my_email = myAccount.get("email")
        my_blocks = myAccount["userInfo"].get("blocks", [])

        # Query sơ bộ: theo department, loại bỏ account bị bạn block
        cursor = AccountRepository.collection.find(
            {
                "userInfo.department": department,
                "email": {"$nin": my_blocks}
            }
        ).limit(20)

        candidates = await cursor.to_list(length=20)

        # Lọc tiếp những account đã block bạn
        results = [
            acc for acc in candidates
            if my_email not in acc["userInfo"].get("blocks", [])
        ]

        return results if results else None

    @staticmethod
    async def find_by_email(email: str) -> Optional[dict]:
        doc = await AccountRepository.collection.find_one({"email": email})
        if doc: return doc
        return None
    
    # @staticmethod
    # async def get_relation_by_email(email: str) -> Optional[dict]:
    #     doc = await AccountRepository.collection.find_one({"email": email})
        
    #     if doc:
    #         return {
    #             'followers': doc.get('userInfo', {}).get('followers', []),
    #             'followed': doc.get('userInfo', {}).get('followed', []),
    #             'blocks': doc.get('userInfo', {}).get('blocks', [])
    #         }
    #     return None

    @staticmethod
    async def get_relation_by_email(email: str) -> Optional[dict]:
        doc = await AccountRepository.collection.find_one({"email": email})

        if not doc:
            return None

        user_info = doc.get('userInfo', {})
        followers = user_info.get('followers', [])
        followed = user_info.get('followed', [])
        blocks = user_info.get('blocks', [])

        # Gom tất cả email cần check status
        all_emails = set(followers + followed + blocks)

        if not all_emails:
            return {
                'followers': [],
                'followed': [],
                'blocks': []
            }

        # Lấy danh sách email còn active
        cursor = AccountRepository.collection.find(
            {
                "email": { "$in": list(all_emails) },
                "status": "active"
            },
            { "email": 1 }
        )
        active_emails = { doc["email"] async for doc in cursor }

        return {
            'followers': [e for e in followers if e in active_emails],
            'followed': [e for e in followed if e in active_emails],
            'blocks': [e for e in blocks if e in active_emails],
        }

    @staticmethod
    async def find_mod() -> list[dict]:
        accounts = []
        query = {
            "role": "Moderator",
            "status": "active",
            "hidden": {"$exists": False} 
        }
        async for account in AccountRepository.collection.find(query):
            accounts.append(account)
        return accounts


    post_collection = db["post"]
    @staticmethod
    async def find_top_suggestions(
        current_user_email: str,
        current_department: Optional[str],
        limit: int
    ) -> list[dict]:
        if not current_department:
            return []

        # ====== BƯỚC 1: Interaction score ======
        posts_pipeline = [
            {
                "$match": {
                    "createdBy": {"$exists": True, "$ne": None},
                    "status": "active"
                }
            },
            {
                "$group": {
                    "_id": "$createdBy",
                    "posts_count": {"$sum": 1}
                }
            }
        ]
        
        posts_count_map = {}
        async for doc in AccountRepository.post_collection.aggregate(posts_pipeline):
            if doc.get("_id"):
                posts_count_map[doc["_id"]] = doc.get("posts_count", 0)

        comments_pipeline = [
            {
                "$match": {
                    "comments": {"$exists": True, "$ne": []},
                    "status": "active"
                }
            },
            {"$unwind": "$comments"},
            {
                "$match": {
                    "comments.commentBy": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$comments.commentBy",
                    "comments_count": {"$sum": 1}
                }
            }
        ]
        
        comments_count_map = {}
        async for doc in AccountRepository.post_collection.aggregate(comments_pipeline):
            if doc.get("_id"):
                comments_count_map[doc["_id"]] = doc.get("comments_count", 0)

        # Merge score
        all_emails = set(posts_count_map.keys()) | set(comments_count_map.keys())
        interaction_scores = {}

        for email in all_emails:
            posts = posts_count_map.get(email, 0)
            comments = comments_count_map.get(email, 0)
            interaction_scores[email] = {
                "posts": posts,
                "comments": comments,
                "score": posts + comments
            }

        # ====== BƯỚC 2 ======
        current_user_doc = await AccountRepository.collection.find_one(
            {"email": current_user_email}
        )

        exclude_emails = {current_user_email}

        if current_user_doc and current_user_doc.get("userInfo", {}).get("followed"):
            followed_list = current_user_doc["userInfo"]["followed"]
            if isinstance(followed_list, list):
                exclude_emails.update(followed_list)

        # ====== BƯỚC 3 ======
        match_conditions = {
            "hidden": {"$exists": False},
            "status": "active",
            "userInfo.department": current_department,
            "email": {
                "$ne": current_user_email,
                "$nin": list(exclude_emails)
            }
        }

        if len(exclude_emails) <= 1:
            match_conditions["email"] = {"$ne": current_user_email}

        accounts = []
        async for account in AccountRepository.collection.find(match_conditions):
            email = account.get("email")
            interaction = interaction_scores.get(email, {
                "posts": 0,
                "comments": 0,
                "score": 0
            })

            account["_interaction_score"] = interaction["score"]
            account["_posts_count"] = interaction["posts"]
            account["_comments_count"] = interaction["comments"]
            accounts.append(account)

        # ====== BƯỚC 4 ======
        accounts.sort(
            key=lambda x: (
                -x["_interaction_score"],
                x.get("userInfo", {}).get("fullName", "") or ""
            )
        )

        result = accounts[:limit]

        return result