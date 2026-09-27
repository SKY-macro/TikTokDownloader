from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from src.interface.creator_search import CreatorSearch
from src.models.search import CreatorSearch as CreatorSearchModel


def make_params():
    return SimpleNamespace(
        headers={},
        logger=Mock(),
        douyin_params=Mock(),
        console=Mock(),
        max_retry=1,
        timeout=10,
        client=AsyncMock(),
        impersonate="chrome",
        user_agent="test",
    )


def test_creator_search_params_match_captured_request():
    search = CreatorSearch(
        make_params(), keyword="健康", from_user="98569634382", offset=10, count=20
    )
    params = search.generate_params()
    assert search.api.endswith("/aweme/v1/web/home/search/item/")
    assert params["search_channel"] == "aweme_personal_home_video"
    assert params["keyword"] == "健康"
    assert params["from_user"] == "98569634382"
    assert params["offset"] == 10
    assert params["count"] == 20


def test_creator_search_normalizes_item_wrapper():
    search = CreatorSearch(make_params(), keyword="健康", from_user="98569634382")
    search.check_response(
        {
            "aweme_list": [{"item": {"aweme_id": "123", "desc": "健康"}}],
            "cursor": 10,
            "has_more": 0,
            "log_pb": {"impr_id": "request-id"},
        },
        "aweme_list",
    )
    assert search.response == [{"aweme_id": "123", "desc": "健康"}]
    assert search.offset == 10
    assert search.search_id == "request-id"
    assert search.finished is True


def test_creator_search_model_accepts_numeric_uid():
    model = CreatorSearchModel(keyword="健康", from_user=98569634382)
    assert model.from_user == "98569634382"


def test_creator_search_model_rejects_sec_uid():
    try:
        CreatorSearchModel(keyword="健康", from_user="MS4wLjABAAAA")
    except ValueError:
        return
    raise AssertionError("non-numeric from_user should be rejected")
