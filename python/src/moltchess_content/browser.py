from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from .types import BrowserLaunchOptions


@dataclass(slots=True)
class BrowserSession:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page
    options: BrowserLaunchOptions

    def goto(self, url: str) -> None:
        self.page.goto(url, wait_until=self.options.wait_until)
        if self.options.ready_selector:
            self.page.locator(self.options.ready_selector).first.wait_for(
                state="visible",
                timeout=self.options.ready_timeout_ms,
            )

    def stop(self) -> None:
        self.browser.close()
        self.playwright.stop()


def start_browser_session(url: str, options: BrowserLaunchOptions | None = None) -> BrowserSession:
    config = options or BrowserLaunchOptions()
    playwright = sync_playwright().start()
    launch_kwargs: dict[str, object] = {"headless": config.headless}
    if config.channel:
        launch_kwargs["channel"] = config.channel
    browser = playwright.chromium.launch(**launch_kwargs)
    context = browser.new_context(
        viewport={"width": config.width, "height": config.height},
        screen={"width": config.width, "height": config.height},
    )
    page = context.new_page()
    session = BrowserSession(
        playwright=playwright,
        browser=browser,
        context=context,
        page=page,
        options=config,
    )
    session.goto(url)
    return session
