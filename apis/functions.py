from fastapi import HTTPException
from security import SECURITY
from playwright_task import AsyncPlaywrightTask, PlaywrightError


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
    except PlaywrightError as e:
        await py_task.close_browser()
        if e.code == "PAYMENT_NOT_FOUND":
            return {"success": False, "message": e.message, "code": e.code}
        raise HTTPException(status_code=400, detail={"success": False, "message": e.message, "code": e.code})
    except Exception as e:
        await py_task.close_browser()
        return {"success": False, "message": str(e), "code": "UNKNOWN_ERROR"}
