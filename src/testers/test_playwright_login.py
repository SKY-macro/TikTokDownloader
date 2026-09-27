from src.tools.playwright_login import cookies_to_dict


def test_cookies_to_dict():
    assert cookies_to_dict(
        [
            {"name": "sessionid_ss", "value": "logged-in"},
            {"name": "uifid", "value": "fingerprint"},
            {"name": "empty", "value": ""},
        ]
    ) == {
        "sessionid_ss": "logged-in",
        "uifid": "fingerprint",
        "empty": "",
    }
