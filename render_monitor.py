import httpx
from datetime import datetime
import asyncio
from schemas import monitor_state, MonitorPayload


async def check_app_status(url: str) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(url), timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            print(f"Error checking {url}: {str(e)}")
            return False
        

async def send_telex_notification(webhook_url: str, message: str):
    payload = {
        "event_name": "Render Inactivity Alert",
        "message": message,
        "status": "success",
        "username": "Render Monitor"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(str(webhook_url), json=payload)
            if response.status_code != 200:
                print(f"Failed to send notification: HTTP {response.status_code}")
        except Exception as e:
            print(f"Failed to send notification: {str(e)}")

async def monitor_app(payload: MonitorPayload):
    app_url = payload.get_setting('app_url')
    webhook_url = payload.get_setting('webhook_url')

    if not app_url or not webhook_url:
        raise ValueError("Missing required settings")

    monitor_state[app_url] = {
        "is_active": True,
        "last_active": datetime.now(),
        "current_status": "starting"
    }

    while app_url in monitor_state:
        try:
            is_active = await check_app_status(app_url)
            current_time = datetime.now()

            state = monitor_state[app_url]
            if is_active:
                state.update({
                    "is_active": True,
                    "last_active": current_time,
                    "current_status": "active"
                })
            else:
                inactive_minutes = (current_time - state["last_active"]).total_seconds() / 60
                if inactive_minutes >= 15:  
                    if state["is_active"]:
                        await send_telex_notification(
                            webhook_url,
                            f"🔴 App {app_url} has been inactive for {int(inactive_minutes)} minutes!"
                        )
                    state.update({
                        "is_active": False,
                        "current_status": "inactive"
                    })
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Error monitoring {app_url}: {str(e)}")
            await asyncio.sleep(60)
