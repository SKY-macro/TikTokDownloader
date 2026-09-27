from asyncio import sleep
from pathlib import Path

from ..translation import _

__all__ = ["DouYinBrowserLogin", "cookies_to_dict"]


def cookies_to_dict(cookies: list[dict]) -> dict[str, str]:
    return {
        item["name"]: item["value"]
        for item in cookies
        if item.get("name") and item.get("value") is not None
    }


class DouYinBrowserLogin:
    """Obtain DouYin cookies through an interactive Chromium login."""

    LOGIN_URL = "https://www.douyin.com/"
    STATE_KEY = "sessionid_ss"

    def __init__(self, console, profile: Path, timeout: int = 300):
        self.console = console
        self.profile = profile
        self.timeout = timeout

    async def run(self) -> dict[str, str]:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            self.console.error(
                _(
                    "扫码登录需要 Playwright；请运行 `uv sync --extra browser-login` 和 "
                    "`uv run playwright install chromium` 后重试。"
                )
            )
            return {}

        self.profile.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                self.profile,
                headless=False,
                locale="zh-CN",
                viewport={"width": 1280, "height": 800},
            )
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(self.LOGIN_URL, wait_until="domcontentloaded")
                self.console.print(
                    _("请在弹出的浏览器中完成验证码和扫码登录，程序会自动检测登录状态。")
                )
                for attempt in range(self.timeout):
                    cookies = await context.cookies(["https://www.douyin.com/"])
                    result = cookies_to_dict(cookies)
                    if result.get(self.STATE_KEY):
                        return result
                    await sleep(1)
                self.console.warning(_("等待扫码登录超时，未写入 Cookie！"))
                return {}
            finally:
                await context.close()
