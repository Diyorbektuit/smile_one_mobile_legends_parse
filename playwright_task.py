import os
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

BROWSER_HEADLESS = False
SESSION_FILE = "session.json"

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(log_dir, "playwright_logs.log"),
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class AsyncPlaywrightTask:
    def __init__(self):
        self.playwright_instance = None
        self.browser = None
        self.page = None

    async def init_browser(self):
        self.playwright_instance = await async_playwright().start()
        self.browser = await self.playwright_instance.chromium.launch(headless=BROWSER_HEADLESS)
        print("🌐 Browser is being created...")

    async def close_browser(self) -> None:
        await self.browser.close()
        await self.playwright_instance.stop()
        print("❌ Browser closed.")

    async def create_page(self):
        if os.path.exists(SESSION_FILE):
            context = await self.browser.new_context(storage_state=SESSION_FILE)
            print("✅ Existing session loaded.")
        else:
            context = await self.browser.new_context()
            print("❗ No session found. Starting new context.")
        self.page = await context.new_page()

    async def login(self, email: str, password: str) -> None:
        await self.page.goto("https://www.smile.one/uz/customer/account/login")

        try:
            async with self.page.expect_popup() as page1_info:
                await self.page.get_by_role("listitem").filter(has_text="Войти в систему через VK").locator("div").click()
            page1 = await page1_info.value
        except PlaywrightTimeoutError:
            raise Exception("❌ VK popup ochilmadi!")

        await page1.locator("label").filter(has_text="Email").click()
        await page1.get_by_role("textbox", name="Email or login").fill(email)
        await page1.get_by_role("button", name="Continue").click()
        await page1.get_by_role("textbox", name="Enter password").fill(password)
        await page1.get_by_role("button", name="Continue").click()

        try:
            await page1.locator("[data-test-id=\"continue-as-button\"]").click()
        except PlaywrightTimeoutError:
            raise Exception("❌ VK login yakunlanmadi!")

        await self.page.context.storage_state(path=SESSION_FILE)
        print("✅ Session saved to file.")

    async def is_logged_in(self) -> bool:
        await self.page.goto("https://www.smile.one/")
        try:
            await self.page.get_by_role("link", name="Entrar").wait_for(timeout=3000)
            print("🔒 Login bo‘lmagan.")
            return False
        except PlaywrightTimeoutError:
            print("🔓 Login bo‘lgan.")
            return True

    async def buy_mobile_legends_diamonds(self, pack_id: int, user_id: int, server_id: int):
        await self.page.goto("https://www.smile.one/merchant/mobilelegends")

        await self.page.get_by_role("textbox", name="USER ID").fill(str(user_id))
        await self.page.get_by_role("textbox", name="ZONE ID").fill(str(server_id))
        await self.page.locator("#smileone-notifi-cancel").click()

        pack_ids = {
            1: "32 2590", 2: "32 2591", 3: "32 2592", 4: "32 2593",
            5: "31 3", 6: "32 3", 7: "32 5", 8: "32 6",
            9: "32 7", 10: "32 8", 11: "32 9", 12: "33 0", 13: "33 3"
        }

        if pack_id not in pack_ids:
            raise ValueError("❌ Pack ID noto‘g‘ri!")
        print(f"📦 Pack tanlangan: {pack_ids[pack_id]}")
        is_break = False
        while not is_break:
            await self.page.locator(f"[id=\"\\{pack_ids[pack_id]}\"]").get_by_role("emphasis").nth(1).click()
            if await self.page.locator(f"[id=\"\\{pack_ids[pack_id]}\"]").is_visible():
                is_break = True

        if await self.page.locator(".smileOneAlert-popUpheader").is_visible():
            raise ValueError("❌ User ID yoki Server ID noto‘g‘ri!")

        # 💳 To‘lov usuli tanlash (birinchi variant)
        await self.page.locator(".payment-method-left").first.click()

        # 🛒 Sotib olish tugmasi
        await self.page.locator("span", has_text="Comprar agora").click()

        # ⚠️ Notifikatsiya bekor qilish (agar chiqsa)
        if await self.page.locator("#smileone-notifi-cancel").is_visible():
            await self.page.locator("#smileone-notifi-cancel").click()

        # ✅ To‘lov muvaffaqiyatli bo‘lganini tekshirish
        try:
            await self.page.get_by_text("Pagamento com sucesso!").wait_for(timeout=5000)
            print("✅ To‘lov muvaffaqiyatli yakunlandi.")
        except PlaywrightTimeoutError:
            raise Exception("❌ To‘lovda xatolik yoki muvaffaqiyatli bo‘lmagan.")

        # 🔁 Davom etish
        await self.page.get_by_role("link", name="Continuar a comprar").click()

