import asyncio
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
        self.popup_page = None

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

        self.popup_page = page1

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
        logging.info("➡️ Sotib olish sahifasiga o'tilmoqda...")
        await self.page.goto("https://www.smile.one/merchant/mobilelegends")

        logging.info(f"🆔 USER ID: {user_id}, SERVER ID: {server_id}")
        await self.page.get_by_role("textbox", name="USER ID").fill(str(user_id))
        await self.page.get_by_role("textbox", name="ZONE ID").fill(str(server_id))

        if await self.page.locator("#smileone-notifi-cancel").is_visible():
            logging.info("🔔 Oldingi bildirishnoma bekor qilinmoqda.")
            await self.page.locator("#smileone-notifi-cancel").click()

        if await self.page.locator(".smileOneAlert-popUpheader").is_visible():
            logging.error("❌ User ID yoki Server ID noto‘g‘ri!")
            raise ValueError("❌ User ID yoki Server ID noto‘g‘ri!")

        logging.info("✅ User ID va Server ID to‘g‘ri kiritildi.")
        await asyncio.sleep(2)

        pack_ids = {
            1: "32 2590", 2: "32 2591", 3: "32 2592", 4: "32 2593",
            5: "31 3", 6: "32 3", 7: "32 5", 8: "32 6",
            9: "32 7", 10: "32 8", 11: "32 9", 12: "33 0", 13: "33 3"
        }

        if pack_id not in pack_ids:
            logging.error(f"❌ Noto‘g‘ri `pack_id` tanlandi: {pack_id}")
            raise ValueError("❌ Noto‘g‘ri `pack_id` tanlandi.")

        pack_selector = f"[id=\"\\{pack_ids[pack_id]}\"]"
        logging.info(f"🎯 Pack tanlanmoqda: ID={pack_id}, selector={pack_selector}")

        try:
            button = self.page.locator(pack_selector).first
            await button.wait_for(timeout=2000)
            await button.scroll_into_view_if_needed()
            await button.hover()
            await button.click()
            logging.info(f"✅ Pack {pack_id} tugmasi bosildi.")
        except PlaywrightTimeoutError:
            logging.error(f"❌ Pack '{pack_ids[pack_id]}' topilmadi sahifada!")
            raise ValueError(f"❌ User ID yoki Server ID noto‘g‘ri bo'lishi mumkin!")

        await self.page.wait_for_timeout(1500)

        if await self.is_read_button_visible():
            logging.info("🔘 Terms & Conditions popup chiqdi.")
            await self.accept_terms_popup_if_visible()

        logging.info("💳 To‘lov usuli tanlanmoqda...")
        await self.page.locator(".payment-method-left").first.click()

        logging.info("🛒 'Comprar agora' tugmasi bosilmoqda...")
        try:
            await self.page.locator("span", has_text="Comprar agora").click()
            logging.info("✅ Xarid qilish bosildi.")
        except PlaywrightTimeoutError:
            logging.error("❌ 'Comprar agora' tugmasi bosilmadi — ustida boshqa element turgan bo'lishi mumkin.")
            raise

        if await self.page.locator("#smileone-notifi-cancel").is_visible():
            logging.info("ℹ️ Bildirishnoma mavjud, yopilmoqda.")
            await self.page.locator("#smileone-notifi-cancel").click()

        logging.info("📦 To‘lov yakunlanmoqda...")
        try:
            await self.page.get_by_text("Pagamento com sucesso!").wait_for(timeout=5000)
            logging.info("✅ To‘lov muvaffaqiyatli yakunlandi.")
        except PlaywrightTimeoutError:
            logging.error("❌ To‘lov yakunlanmadi.")
            raise Exception("❌ To‘lovda xatolik yoki muvaffaqiyatli bo‘lmagan.")

        logging.info("🔁 Davom etish uchun 'Continuar a comprar' tugmasi bosilmoqda...")
        await self.page.get_by_role("link", name="Continuar a comprar").click()

    async def is_read_button_visible(self) -> bool:
        return await self.page.locator("#readbutton").is_visible()

    async def accept_terms_popup_if_visible(self):
        read_button = self.page.locator("#readbutton")
        if await read_button.is_visible():
            print("⚠️ 'I have read' tugmasi ko‘rindi — bosilmoqda...")
            await read_button.scroll_into_view_if_needed()
            await read_button.click()
            await self.page.wait_for_timeout(500)  # modal yopilishi uchun ozgina kutish
            print("✅ 'I have read' tugmasi bosildi va yopildi.")
        else:
            print("ℹ️ 'I have read' tugmasi mavjud emas — davom etiladi.")

    # async def continue_as_if_needed(self):
    #     print("🔎 'Продолжить как ...' tugmasi bor yo'qmi tekshirilmoqda...")
    #     """
    #     Agar 'Продолжить как ...' tugmasi mavjud bo‘lsa, uni bosib davom etadi.
    #     """
    #     continue_button = self.popup_page.locator("[data-test-id='continue-as-button']")
    #     if await continue_button.is_visible():
    #         logging.info("➡️ 'Продолжить как ...' tugmasi mavjud — bosilmoqda.")
    #         await continue_button.scroll_into_view_if_needed()
    #         await continue_button.click()
    #         await self.popup_page.wait_for_timeout(1000)
    #         logging.info("✅ 'Продолжить как ...' tugmasi bosildi.")
    #         return True
    #     else:
    #         logging.info("ℹ️ 'Продолжить как ...' tugmasi mavjud emas — davom etiladi.")
    #         await asyncio.sleep(100)
    #         return False

