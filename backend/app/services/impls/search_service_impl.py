from typing import List, Optional
from dto.search.request.search_account_request import SearchAccountRequest
from dto.search.request.search_post_request import SearchPostRequest
from dto.search.response.search_account_response import SearchAccountResponse
from dto.search.response.search_post_response import SearchPostResponse
from models.account_model import Account
from models.base_model import bson_to_dict
from models.post_model import Post
from repositories.account_repository import AccountRepository
from repositories.post_repository import PostRepository
from services.interfaces.search_service_interface import ISearchService



class SearchServiceImpl(ISearchService):
    
    async def search_account(self, req: SearchAccountRequest) -> Optional[SearchAccountResponse]:
        dic_acc = await AccountRepository.find_by_email(req.email)
        list_dic = await AccountRepository.find_by_fullname(req.keySearch, dic_acc)
        list_rs: List[Account] = []
        if list_dic:
            for dic in list_dic:
                acc: Account = Account(**bson_to_dict(dic))
                list_rs.append(acc)
        # lấy các tài khoản cùng khoa
        # else:
        #     acc_dep: Account = Account(**bson_to_dict(dic_acc))
        #     list_acc_dep = await AccountRepository.find_by_department(acc_dep.userInfo.department, dic_acc)
        #     if list_acc_dep:
        #         for dep in list_acc_dep:
        #             acc_depp: Account = Account(**bson_to_dict(dep))
        #             list_rs.append(acc_depp)
        return SearchAccountResponse(account_list=list_rs)

    async def search_post(self, req: SearchPostRequest) -> Optional[SearchPostResponse]:
        dic_account = await AccountRepository.find_by_email(req.email)
        account: Account = Account(**bson_to_dict(dic_account))
        list_dic = await PostRepository.find_post_by_keysearch_and_department(req.keySearch, account.userInfo.department, dic_account)
        list: List[Post] = []
        for dic in list_dic:
            post: Post = Post(**bson_to_dict(dic))
            list.append(post)
        return SearchPostResponse(post_list=list)



    