import httpx
from datetime import datetime
import asyncio
from schemas import App, monitor_state


async def check_app_status(url: str) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(url), timeout=5.0)
            return response.status_code == 200
        except Exception:
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
            if response.status_code == 200:
                print(f"Telex notification sent: {message}")
            else:
                print(f"Failed to send Telex notification, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send notification: {e}")

async def monitor_app(app: App):
    app_url = str(app.app_url)
    print(f"Started monitoring {app_url}")

    while app_url in monitor_state:
        is_active = await check_app_status(app_url)
        print(f"App {app_url} status: {is_active}")
        current_time = datetime.now()

        if not is_active:
            inactive_duration = current_time - monitor_state[app_url]["last_active"]
        
            if (inactive_duration.total_seconds() / 60) >= app.inactivity_threshold:
                if monitor_state[app_url]["is_active"]:
                    await send_telex_notification(
                        str(app.webhook_url),
                        f"🔴 App {app_url} has been inactive for {app.inactivity_threshold} minutes!"
                    )
                monitor_state[app_url].update({
                    "is_active": False,
                    "current_status": "inactive"
                })

        await asyncio.sleep(60)
