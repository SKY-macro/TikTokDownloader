from typing import TYPE_CHECKING, Union
from urllib.parse import quote

from src.interface.template import API

if TYPE_CHECKING:
    from src.config import Parameter
    from src.testers import Params


class CreatorSearch(API):
    """Search published works within a single DouYin creator profile."""

    def __init__(
        self,
        params: Union["Parameter", "Params"],
        cookie: str = "",
        proxy: str | None = None,
        keyword: str = ...,
        from_user: str = ...,
        pages: int = 1,
        offset: int = 0,
        count: int = 10,
        sort_type: int = 0,
        publish_time: int = 0,
        *args,
        **kwargs,
    ):
        super().__init__(params, cookie, proxy, *args, **kwargs)
        self.api = f"{self.domain}aweme/v1/web/home/search/item/"
        self.keyword = keyword
        self.from_user = str(from_user)
        self.pages = pages
        self.offset = offset
        self.count = count
        self.sort_type = sort_type
        self.publish_time = publish_time
        self.search_id = None
        self.text = "作者作品搜索"

    def generate_params(self) -> dict:
        params = self.params | {
            "search_channel": "aweme_personal_home_video",
            "search_source": "normal_search",
            "search_scene": "douyin_search",
            "sort_type": self.sort_type,
            "publish_time": self.publish_time,
            "is_filter_search": "1" if self.sort_type or self.publish_time else "0",
            "query_correct_type": "1",
            "keyword": self.keyword,
            "enable_history": "1",
            "offset": self.offset,
            "count": self.count,
            "from_user": self.from_user,
            "version_code": "170400",
            "version_name": "17.4.0",
        }
        if self.search_id:
            params["search_id"] = self.search_id
        return params

    async def run(self, single_page=False, *args, **kwargs):
        self.set_referer(f"{self.domain}user/{quote(self.from_user)}")
        return await super().run(
            single_page=single_page,
            data_key="aweme_list",
            params=self.generate_params,
            *args,
            **kwargs,
        )

    def check_response(
        self,
        data_dict: dict,
        data_key: str,
        error_text="",
        cursor="cursor",
        has_more="has_more",
        *args,
        **kwargs,
    ):
        rows = data_dict.get(data_key)
        if not isinstance(rows, list):
            self.log.warning(error_text)
            self.finished = True
            return
        if not rows:
            if not self.response:
                self.response.append([])
            self.finished = True
            return
        self.offset = data_dict.get(cursor, self.offset + len(rows))
        self.search_id = (data_dict.get("log_pb") or {}).get("impr_id")
        self.append_response([row.get("item", row) for row in rows])
        self.finished = not data_dict.get(has_more)
