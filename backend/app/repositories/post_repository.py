from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from core.database import db
from bson import ObjectId
import re
from rapidfuzz import fuzz

from models.post_model import React
from repositories.account_repository import AccountRepository


class PostRepository:

    collection = db["post"]

    @staticmethod
    async def insert(data: dict) -> dict:
        result = await PostRepository.collection.insert_one(data)
        new_post = await PostRepository.collection.find_one({"_id": result.inserted_id})
        return new_post

    @staticmethod
    async def find_all() -> list[dict]:
        posts = []
        async for post in PostRepository.collection.find():
            posts.append(post)
        return posts

    @staticmethod
    async def find_by_id(post_id: str) -> dict | None:
        return await PostRepository.collection.find_one({"_id": ObjectId(post_id)})

    @staticmethod
    async def update(data: dict) -> dict | None:
        post_id = data.pop("id", None)
        if not post_id: return None
        await PostRepository.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": data}
        )
        return await PostRepository.find_by_id(post_id)

    @staticmethod
    async def delete(post_id: str) -> bool:
        result = await PostRepository.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"status": "off"}}
        )
        return result.modified_count > 0

    @staticmethod
    async def update_comment_status(post_id: str, comment_id: str, status: str):
        result = await PostRepository.collection.update_one(
            {"_id": ObjectId(post_id), "comments.commentId": comment_id}, 
            {"$set": {"comments.$.statusComment": status}} 
        )

        if result.modified_count == 0:
            return None

        updated_post = await PostRepository.find_by_id(post_id)
        return updated_post
    
    # @staticmethod
    # async def get_ranked_posts(
    #     email: str,
    #     followed: List[str],
    #     interacted: List[str],
    #     user_dept: Optional[str],
    #     exclude_ids: List[str],
    #     limit: int,
    #     myAccount: dict
    # ) -> List[dict]:
    #     from bson import ObjectId
    #     from datetime import datetime, timezone, timedelta

    #     now = datetime.now(timezone.utc)
    #     today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #     today_end = today_start + timedelta(days=1)

    #     my_blocks = myAccount["userInfo"].get("blocks", [])
    #     # my_followers = set(myAccount["userInfo"].get("followers", []))
    #     my_followed = set(myAccount["userInfo"].get("followed", []))
    #     # mutual_follow = list(my_followers.intersection(my_followed))
    #     mutual_follow = list(my_followed)

    #     # --- 1. Match stage: public hoặc follow mutual + loại post blocked ---
    #     match_stage = {
    #         "status": "active",
    #         "$or": [
    #             # public nhưng không nằm trong blocks
    #             {"visibility": "public", "createdBy": {"$nin": my_blocks}},
    #             # follow nhưng author nằm trong mutual_follow
    #             {"visibility": "follow", "createdBy": {"$in": mutual_follow}}
    #         ]
    #     }
    #     if exclude_ids:
    #         match_stage["_id"] = {"$nin": [ObjectId(pid) for pid in exclude_ids]}

    #     # --- 2. Pipeline ---
    #     pipeline = [
    #         {"$match": match_stage},
    #         # --- Lookup để lấy thông tin blocks của author ---
    #         {
    #             "$lookup": {
    #                 "from": "account",
    #                 "localField": "createdBy",
    #                 "foreignField": "email",
    #                 "as": "author_info"
    #             }
    #         },
    #         {"$unwind": "$author_info"},
    #         # Mutual block: loại bỏ nếu author block bạn
    #         {"$match": {
    #             "$expr": {"$not": {"$in": [email, {"$ifNull": ["$author_info.userInfo.blocks", []]}]}}
    #         }},
    #         # Tính hotScore, finalScorez
    #         {"$addFields": {
    #             "hotScore": {
    #                 "$add": [
    #                     {"$size": {"$ifNull": ["$react.love", []]}},
    #                     {"$multiply": [1.5, {"$size": {"$ifNull": ["$react.like", []]}}]},
    #                     {"$multiply": [1.2, {"$size": {"$ifNull": ["$react.haha", []]}}]},
    #                     {"$multiply": [1.2, {"$size": {"$ifNull": ["$react.wow", []]}}]},
    #                     {"$multiply": [0.8, {"$size": {"$ifNull": ["$react.sad", []]}}]},
    #                     {"$multiply": [0.5, {"$size": {"$ifNull": ["$react.angry", []]}}]},
    #                     {"$size": {"$ifNull": ["$comments", []]}}
    #                 ]
    #             },
    #             "isMyPostToday": {
    #                 "$and": [
    #                     {"$eq": ["$createdBy", email]},
    #                     {"$gte": ["$createdAt", today_start]},
    #                     {"$lt": ["$createdAt", today_end]}
    #                 ]
    #             },
    #             "isFollowed": {"$in": ["$createdBy", followed]},
    #             "isInteracted": {"$in": ["$createdBy", interacted]},
    #             "sameDept": {"$in": [user_dept, {"$ifNull": ["$category", []]}]},
    #             "ageHours": {"$divide": [{"$subtract": [now, "$createdAt"]}, 3600000]}
    #         }},
    #         {"$addFields": {
    #             "finalScore": {
    #                 "$add": [
    #                     {"$cond": ["$isMyPostToday", 1_000_000, 0]},
    #                     {"$cond": ["$isFollowed", 300, 0]},
    #                     {"$cond": ["$isInteracted", 200, 0]},
    #                     {"$cond": ["$sameDept", 100, 0]},
    #                     "$hotScore",
    #                     {"$divide": [100, {"$add": ["$ageHours", 4]}]}
    #                 ]
    #             }
    #         }},
    #         {"$sort": {"finalScore": -1}},
    #         {"$limit": limit or 10_000},
    #         {"$project": {
    #             "finalScore": 0, "hotScore": 0, "isMyPostToday": 0,
    #             "isFollowed": 0, "isInteracted": 0, "sameDept": 0, "ageHours": 0,
    #             "author_info": 0
    #         }}
    #     ]

    #     print(f"[REPO] pipeline limit = {limit}, exclude_ids = {len(exclude_ids)}")
    #     result = await PostRepository.collection.aggregate(pipeline).to_list(length=limit)
    #     print(f"[REPO] returned = {len(result)}")
    #     return result
    @staticmethod
    async def get_ranked_posts(
        email: str,
        followed: List[str],
        interacted: List[str],
        user_dept: Optional[str],
        exclude_ids: List[str],
        limit: int,
        myAccount: dict
    ) -> List[dict]:
        from bson import ObjectId
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        my_blocks = myAccount["userInfo"].get("blocks", [])
        my_followed = set(myAccount["userInfo"].get("followed", []))
        mutual_follow = list(my_followed)

        # --- 1. Match stage ---
        match_stage = {
            "status": "active",
            "$or": [
                {"visibility": "public", "createdBy": {"$nin": my_blocks}},
                {"visibility": "follow", "createdBy": {"$in": mutual_follow}}
            ]
        }
        if exclude_ids:
            match_stage["_id"] = {"$nin": [ObjectId(pid) for pid in exclude_ids]}

        # --- 2. Pipeline ---
        pipeline = [
            {"$match": match_stage},
            {
                "$lookup": {
                    "from": "account",
                    "localField": "createdBy",
                    "foreignField": "email",
                    "as": "author_info"
                }
            },
            {"$unwind": "$author_info"},
            {"$match": {
                "$expr": {"$not": {"$in": [email, {"$ifNull": ["$author_info.userInfo.blocks", []]}]}}
            }},
            {"$addFields": {
                # tieBreaker random để xáo trộn bài cùng điểm mỗi lần reload
                "tieBreaker": {"$rand": {}},
                "hotScore": {
                    "$add": [
                        {"$size": {"$ifNull": ["$react.love", []]}},
                        {"$multiply": [1.5, {"$size": {"$ifNull": ["$react.like", []]}}]},
                        {"$multiply": [1.2, {"$size": {"$ifNull": ["$react.haha", []]}}]},
                        {"$multiply": [1.2, {"$size": {"$ifNull": ["$react.wow", []]}}]},
                        {"$multiply": [0.8, {"$size": {"$ifNull": ["$react.sad", []]}}]},
                        {"$multiply": [0.5, {"$size": {"$ifNull": ["$react.angry", []]}}]},
                        {"$size": {"$ifNull": ["$comments", []]}}
                    ]
                },
                "isMyPostToday": {
                    "$and": [
                        {"$eq": ["$createdBy", email]},
                        {"$gte": ["$createdAt", today_start]},
                        {"$lt": ["$createdAt", today_end]}
                    ]
                },
                "isFollowed": {"$in": ["$createdBy", followed]},
                "isInteracted": {"$in": ["$createdBy", interacted]},
                "sameDept": {"$in": [user_dept, {"$ifNull": ["$category", []]}]},
                "ageHours": {"$divide": [{"$subtract": [now, "$createdAt"]}, 3600000]}
            }},
            {"$addFields": {
                "finalScore": {
                    "$add": [
                        {"$cond": ["$isMyPostToday", 1_000_000, 0]},
                        {"$cond": ["$isFollowed", 300, 0]},
                        {"$cond": ["$isInteracted", 200, 0]},
                        {"$cond": ["$sameDept", 100, 0]},
                        "$hotScore",
                        {"$divide": [100, {"$add": ["$ageHours", 4]}]}
                    ]
                }
            }},
            # Sort finalScore giảm dần, cùng điểm thì random theo tieBreaker
            {"$sort": {"finalScore": -1, "tieBreaker": 1}},
            {"$limit": limit or 10_000},
            {"$project": {
                "finalScore": 0, "hotScore": 0, "isMyPostToday": 0,
                "isFollowed": 0, "isInteracted": 0, "sameDept": 0, "ageHours": 0,
                "tieBreaker": 0, "author_info": 0
            }}
        ]

        # print(f"[REPO] pipeline limit = {limit}, exclude_ids = {len(exclude_ids)}")
        result = await PostRepository.collection.aggregate(pipeline).to_list(length=limit)
        # print(f"[REPO] returned = {len(result)}")
        return result


    @staticmethod
    async def update_react(post_id: str, react: React) -> dict | None:
            """
            Cập nhật trường 'react' của bài viết theo ID.
            """
            # Chuyển React instance thành dict
            react_dict = react.dict()

            await PostRepository.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"react": react_dict}}
            )
            return await PostRepository.find_by_id(post_id)
    
    @staticmethod
    async def find_by_email(email: str, ownerEmail: str) -> List[Dict]:
        posts = []

        # 🔥 CASE 1: Chủ bài tự xem bài của mình
        if email == ownerEmail:
            query = {
                "createdBy": email,
                "status": "active"
            }

            async for post in (
                PostRepository.collection
                .find(query)
                .sort("createdAt", -1)
            ):
                posts.append(post)

            return posts

        # 🔥 CASE 2: Người khác xem bài
        account = await AccountRepository.collection.find_one(
            {"email": email},
            {"userInfo.followers": 1}
        )

        followers = []
        if account and "userInfo" in account:
            followers = account["userInfo"].get("followers", [])

        allowed_visibilities = ["public"]

        if ownerEmail in followers:
            allowed_visibilities.append("follow")

        query = {
            "createdBy": email,
            "status": "active",
            "visibility": {"$in": allowed_visibilities}
        }

        async for post in (
            PostRepository.collection
            .find(query)
            .sort("createdAt", -1)
        ):
            posts.append(post)

        return posts


    # @staticmethod
    # async def find_post_by_keysearch_and_department(
    #     keySearch: str,
    #     department: str,
    #     myAccount: dict
    # ) -> Optional[list[dict]]:

    #     from rapidfuzz import fuzz

    #     my_email = myAccount.get("email")
    #     # Lấy danh sách email follow 2 chiều
    #     my_followed = set(myAccount["userInfo"].get("followed", []))
    #     # mutual_follow = list(my_followers.intersection(my_followed))
    #     mutual_follow = list(my_followed)

    #     # Danh sách email bị block bởi tài khoản đang search
    #     my_blocks = myAccount["userInfo"].get("blocks", [])

    #     # Visibility conditions
    #     visibility_condition = {
    #         "$or": [
    #             # PUBLIC nhưng không phải của account bạn đã block
    #             {
    #                 "visibility": "public",
    #                 "createdBy": {"$nin": my_blocks}
    #             },
    #             # FOLLOW nhưng phải mutual follow
    #             {
    #                 "visibility": "follow",
    #                 "createdBy": {"$in": mutual_follow}
    #             }
    #         ]
    #     }

    #     # 1. Tách keySearch thành từ
    #     parts = keySearch.lower().split()

    #     # 2. Regex sơ bộ
    #     regex_conditions = [
    #         {
    #             "$or": [
    #                 {"title": {"$regex": part[:2], "$options": "i"}},
    #                 {"content": {"$regex": part[:2], "$options": "i"}},
    #             ]
    #         }
    #         for part in parts if len(part) >= 2
    #     ]

    #     # 3. Query các post ứng viên theo regex + visibility
    #     cursor = PostRepository.collection.find({
    #         "$or": regex_conditions,
    #         "status": "active",
    #         **visibility_condition
    #     })

    #     candidates = await cursor.to_list(length=None)

    #     # 4. Fuzzy filter + mutual block check
    #     matched = []
    #     for post in candidates:
    #         # Lấy thông tin account tạo post để kiểm tra mutual block
    #         author = await AccountRepository.collection.find_one({"email": post.get("createdBy")})
    #         if not author:
    #             continue

    #         author_blocks = author["userInfo"].get("blocks", [])
    #         # Nếu author đã block bạn → skip
    #         if my_email in author_blocks:
    #             continue

    #         # Fuzzy match
    #         title = post.get("title", "").lower()
    #         content = post.get("content", "").lower()
    #         score = max(
    #             fuzz.token_sort_ratio(title, keySearch.lower()),
    #             fuzz.token_sort_ratio(content, keySearch.lower())
    #         )
    #         if score >= 50:
    #             matched.append(post)

    #     # Sort theo createdAt giảm dần
    #     if matched:
    #         matched.sort(key=lambda p: p.get("createdAt"), reverse=True)
    #         return matched

    #     # Nếu không có bài viết nào phù hợp với keySearch và các điều kiện visibility, return None
    #     return None
    _CLEAN_RE = re.compile(r"[^\w\s\u00C0-\u024F\u1E00-\u1EFF]", re.UNICODE)

    @classmethod
    def extract_keywords(cls, text: str) -> list[str]:
        if not text:
            return []
        cleaned = cls._CLEAN_RE.sub(" ", text.lower())
        seen = set()
        result = []
        for w in cleaned.split():
            if len(w) >= 2 and w not in seen:
                seen.add(w)
                result.append(w)
        return result

    @classmethod
    def calc_score(cls, keywords: list[str], title: str, content: str, search_text: str) -> float:
        if not keywords:
            return 0.0
        t, c = title.lower(), content.lower()
        kw_scores = [max(fuzz.partial_ratio(k, t), fuzz.partial_ratio(k, c)) for k in keywords]
        avg_kw = sum(kw_scores) / len(kw_scores)
        max_kw = max(kw_scores)
        full = max(fuzz.token_set_ratio(t, search_text), fuzz.token_set_ratio(c, search_text))
        return max(avg_kw * 0.7 + max_kw * 0.3, full * 0.85)

    @staticmethod
    async def find_post_by_keysearch_and_department(
        keySearch: str,
        department: str,  # Department của người đang search (dùng để ưu tiên/loại?)
        myAccount: dict,
    ) -> list[dict]:

        my_email = myAccount.get("email")
        my_followed = set(myAccount.get("userInfo", {}).get("followed", []))
        my_blocks = myAccount.get("userInfo", {}).get("blocks", [])

        keywords = PostRepository.extract_keywords(keySearch)
        if not keywords:
            return []

        # Visibility conditions
        visibility = [
            {"visibility": "public", "createdBy": {"$nin": my_blocks}},
            {"visibility": "follow", "createdBy": {"$in": list(my_followed)}},
        ]

        # Regex: mỗi keyword match title hoặc content
        regex_conds = [
            {"$or": [
                {"title": {"$regex": kw, "$options": "i"}},
                {"content": {"$regex": kw, "$options": "i"}},
            ]}
            for kw in keywords
        ]

        query = {"$and": [
            {"$or": regex_conds},
            {"status": "active"},
            {"$or": visibility},
        ]}

        candidates = await PostRepository.collection.find(query).to_list(length=None)

        matched = []
        search_lower = keySearch.lower()

        for post in candidates:
            author_email = post.get("createdBy")
            if not author_email:
                continue

            # Lấy thông tin author để check mutual block + department
            author = await AccountRepository.collection.find_one(
                {"email": author_email},
                {"userInfo.blocks": 1, "userInfo.department": 1}
            )
            if not author:
                continue

            # Mutual block check
            author_blocks = author.get("userInfo", {}).get("blocks", [])
            if my_email in author_blocks:
                continue

            # NẾU muốn filter theo department của author (không phải của post)
            # Bỏ comment đoạn này nếu cần:
            # author_dept = author.get("userInfo", {}).get("department", "")
            # if department and department.strip():
            #     if author_dept.upper() != department.strip().upper():
            #         continue  # Skip post của author khác department

            # Score
            score = PostRepository.calc_score(
                keywords,
                post.get("title", ""),
                post.get("content", ""),
                search_lower
            )

            if score >= 50:
                post["_score"] = score
                # Thêm department của author vào kết quả để FE hiển thị
                post["_authorDepartment"] = author.get("userInfo", {}).get("department", "")
                matched.append(post)

        matched.sort(
            key=lambda p: (p.pop("_score", 0), p.get("createdAt", "")),
            reverse=True
        )

        # Dọn dẹp field tạm
        for p in matched:
            p.pop("_authorDepartment", None)

        return matched

    @staticmethod
    async def get_post_of_day() -> int:
        now = datetime.now(timezone.utc)
        start_of_day = datetime(now.year, now.month, now.day)
        end_of_day = start_of_day + timedelta(days=1) - timedelta(microseconds=1)

        posts_today = await PostRepository.collection.find({
            'createdAt': {
                '$gte': start_of_day,
                '$lte': end_of_day
            }
        }).to_list(None) 
        return len(posts_today)
    
    @staticmethod
    async def get_top_interacted_posts_in_week(limit: int = 10) -> List[dict]:
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=7)

        posts = await PostRepository.collection.find({
            'createdAt': {'$gte': start_of_week},
            'status': 'active'
        }).to_list(length=None)

        def calculate_interaction_score(post: dict) -> int:
            react_score = sum([
                len(post.get('react', {}).get(react_type, []))
                for react_type in ['love', 'like', 'haha', 'wow', 'sad', 'angry']
            ])
            comment_score = len(post.get('comments', []))
            return react_score + comment_score

        post_dic = []
        for post in posts:
            post_dic.append(post)

        post_dic.sort(key=calculate_interaction_score, reverse=True)
        top_posts = post_dic[:limit]

        result = [
            {
                "postId": str(post["_id"]),
                "title": post.get("title", ""),
                "createdBy": post.get("createdBy", ""),
                "interactions": calculate_interaction_score(post)
            }
            for post in top_posts
        ]

        return result
    
    @staticmethod
    def department_to_email(department: str) -> str:
        mapping = {
            "CHÍNH TRỊ LUẬT": "ctl.hcmute@utezone.com",
            "CƠ KHÍ CHẾ TẠO MÁY": "ckctm.hcmute@utezone.com",
            "CƠ KHÍ ĐỘNG LỰC": "ckdl.hcmute@utezone.com",
            "CÔNG NGHỆ HÓA HỌC VÀ THỰC PHẨM": "cnhtp.hcmute@utezone.com",
            "CÔNG NGHỆ THÔNG TIN": "cntt.hcmute@utezone.com",
            "ĐIỆN - ĐIỆN TỬ": "dtdt.hcmute@utezone.com",
            "IN VÀ TRUYỀN THÔNG": "intt.hcmute@utezone.com",
            "KHOA HỌC ỨNG DỤNG": "khud.hcmute@utezone.com",
            "KINH TẾ": "kt.hcmute@utezone.com",
            "NGOẠI NGỮ": "nn.hcmute@utezone.com",
            "THỜI TRANG VÀ DU LỊCH": "ttdl.hcmute@utezone.com",
            "XÂY DỰNG": "xd.hcmute@utezone.com",
            "VIỆN SƯ PHẠM KỸ THUẬT": "vspkt.hcmute@utezone.com"
        }

        return mapping.get(department, "")

    @staticmethod
    async def get_post_suggest(email: str) -> List[Dict]:
        posts = []

        # 1. Tìm account theo email truyền vào
        account = await AccountRepository.collection.find_one(
            {"email": email, "status": "active"}
        )
        
        if not account:
            return posts

        # 2. Lấy department của account
        department = account.get("userInfo", {}).get("department", "")
        department_email = PostRepository.department_to_email(department)
        
        # 3. Lấy bài post mới nhất của hcmute
        hcmute_post = await PostRepository.collection.find_one(
            {
                "createdBy": "hcmute@utezone.com",
                "status": "active"
            },
            sort=[("createdAt", -1)]
        )

        if hcmute_post:
            posts.append(hcmute_post)

        # 4. Lấy bài post mới nhất của khoa (department)
        if department_email:
            department_post = await PostRepository.collection.find_one(
                {
                    "createdBy": department_email,
                    "status": "active"
                },
                sort=[("createdAt", -1)]
            )

            if department_post:
                posts.append(department_post)

        return posts

    @staticmethod
    async def get_post_hidden_by_email(email: str) -> List[Dict]:
        posts = []

        query = {"createdBy": email, "status": "off"}    

        async for post in (
            PostRepository.collection
            .find(query)
            .sort("createdAt", -1)
        ):
            posts.append(post)
        return posts