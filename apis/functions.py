from fastapi import HTTPException
from security import SECURITY
from playwright_task import AsyncPlaywrightTask


async def take_diamond(user_id: int, item_id: int, server_id: int):
    py_task = AsyncPlaywrightTask()
    await py_task.init_browser()
    await py_task.create_page()
    try:
        is_logged_in = await py_task.is_logged_in()
        if not is_logged_in:
            await py_task.login(email=SECURITY.WK_EMAIL, password=SECURITY.WK_PASSWORD)
        await py_task.buy_mobile_legends_diamonds(pack_id=item_id, server_id=server_id, user_id=user_id)
        await py_task.close_browser()
        return {"success": True}
    except Exception as e:
        await py_task.close_browser()
        raise HTTPException(status_code=400, detail=f"Transaction error: {str(e)}")
