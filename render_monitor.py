import httpx
from datetime import datetime, timedelta
import asyncio
from schemas import MonitorPayload


async def check_app_status(url: str) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(url), timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            print(f"Error checking {url}: {str(e)}")
            return False
        

async def monitor_app(payload: MonitorPayload):
    app = []
    for setting in payload.settings:
        if setting.label.startswith("app"):
            app_url = setting.default
            if app_url:
                app.append({
                    "url": app_url,
                    "is_active": True,
                    "last_active": datetime.now(),
                    "down_since": None,
                    "next_check_time": datetime.now()  
                })
    
    if not app:
        raise ValueError("No app URLs provided in settings")
    
    webhook_url = payload.return_url
    
    if 'return' in webhook_url:
        webhook_url = webhook_url.replace('/v1/return/', '/v1/webhooks/')
    
    print(f"Monitoring App: {[a['url'] for a in app]}")
    print(f"Using webhook URL: {webhook_url}")
    
    while True:
        try:
            current_time = datetime.now()
            
            for app_info in app:
                
                if app_info["is_active"] and current_time < app_info["next_check_time"]:
                    continue
                
                try:
                    is_active = await asyncio.wait_for(
                        check_app_status(app_info["url"]),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    is_active = False
                
                if is_active:
                    # App is active - set next check time to 15 minutes from now
                    if not app_info["is_active"]:
                        print(f"App {app_info['url']} is back online")
                    
                    app_info.update({
                        "is_active": True,
                        "last_active": current_time,
                        "down_since": None,
                        "next_check_time": current_time + timedelta(minutes=15)
                    })
                else:
                    
                    if app_info["is_active"]:
                       
                        app_info.update({
                            "is_active": False,
                            "down_since": current_time
                        })
                    
                    
                    message = (
                        f"🔴 App {app_info['url']} is inactive (no response in 5 seconds)\n"
                        # f"Down since: {app_info['down_since'].strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    try:
                        await send_telex_notification(
                            webhook_url=webhook_url,
                            message=message,
                            status="error"
                        )
                        print(f"Notification sent for {app_info['url']}")
                    except Exception as e:
                        print(f"Failed to send notification: {e}")
            
            await asyncio.sleep(60) 
            
        except Exception as e:
            print(f"Error during monitoring: {e}")
            await asyncio.sleep(60)

async def send_telex_notification(webhook_url: str, message: str, status: str = "error"):
    payload = {
        "event_name": "Render Inactivity Alert",
        "message": message,
        "status": status,
        "username": "Render Monitor"
    }

    print(f"Sending notification: {payload}")  

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Notification response: {response.status_code}")
            if response.status_code != 200:
                print(f"Failed to send notification: {response.text}")
        except Exception as e:
            print(f"Error sending notification: {e}")