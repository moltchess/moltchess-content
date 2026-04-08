import { chromium } from "playwright";
import type { BrowserSession, BrowserLaunchOptions } from "./types.js";

export async function startBrowserSession(url: string, options: BrowserLaunchOptions = {}): Promise<BrowserSession> {
  const viewport = options.viewport ?? { width: 1920, height: 1080 };
  const browser = await chromium.launch({
    headless: options.headless ?? true,
    ...(options.channel ? { channel: options.channel } : {}),
  });
  const context = await browser.newContext({
    viewport,
    screen: viewport,
  });
  const page = await context.newPage();

  const goto = async (nextUrl: string) => {
    await page.goto(nextUrl, { waitUntil: options.waitUntil ?? "networkidle" });
    if (options.readySelector) {
      await page.locator(options.readySelector).first().waitFor({
        state: "visible",
        timeout: options.readyTimeoutMs ?? 30_000,
      });
    }
  };

  await goto(url);

  return {
    browser,
    context,
    page,
    goto,
    close: async () => {
      await browser.close();
    },
  };
}
