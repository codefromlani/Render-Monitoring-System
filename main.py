from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from schemas import App, MonitoringStatus, monitor_state
from render_monitor import monitor_app  
from datetime import datetime
from typing import List


app = FastAPI(
    title="Render Monitor", 
    description="Monitor Render apps for inactivity"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://staging.telextest.im", "http://telextest.im", "https://staging.telex.im", "https://telex.im"], # NB: telextest is a local url
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


# @app.post("/monitor/start")
@app.post("/tick")
async def start_monitoring(app: App, background_tasks: BackgroundTasks):
    app_url = str(app.app_url)

    if app_url in monitor_state:
        raise HTTPException(
            status_code=400, 
            detail="App is already being monitored"
        )

    monitor_state[app_url] = {
        "is_active": True,
        "last_active": datetime.now(),
        "current_status": "starting"
    }

    background_tasks.add_task(monitor_app, app)
    return {"status": "started", "app": app_url}


# Add / at the of the url (e.g "https://e-library-api-system.onrender.com/")
@app.post("/monitor/stop", response_model=dict)
async def stop_monitoring(app_url: str):
    if app_url not in monitor_state:
        raise HTTPException(
            status_code=404, 
            detail=f"App {app_url} not found in monitoring list"
        )
    
    monitor_state.pop(app_url)
    return {
        "status": "stopped", 
        "app": app_url
    }
    

@app.get("/monitor/status")
async def get_all_status() -> List[MonitoringStatus]:
    """Get status of all monitored sites"""
    return [
        MonitoringStatus(
            app_url=url,
            last_active=state["last_active"],
            is_active=state["is_active"],
            current_status=state["current_status"]
        )
        for url, state in monitor_state.items()
    ]


@app.get("/integration.json")
async def get_json_settings():
    integration_settings = {
        "data": {
            "date": {
                "created_at": "2025-02-19",
                "updated_at": "2025-02-19"
            },
            "descriptions": {
                "app_description": "An automated monitoring system that tracks web app activity status on render free tier.",
                "app_logo": "https://img.freepik.com/fotos-premium/ilustracao-de-renderizacao-3d-on-line-de-rastreamento-de-entrega_7209-806.jpg?w=996",
                "app_name": "Render Inactivity Alert.",
                "app_url": "https://render-monitor-kk3h.onrender.com",
                "background_color": "#HEXCODE"
            },
            "integration_category": "Monitoring & Logging",
            "integration_type": "interval",
            "is_active": False,
            "key_features": [
                "- Monitor Render apps for inactivity"
            ],
            "author": "Rodiat Hammed",
            "settings": [
                {
                    "label": "app_url",
                    "type": "text",
                    "description": "URL of your Render-hosted application to monitor",
                    "required": True,
                    "default": ""
                },
                {
                    "label": "webhook_url",
                    "type": "text",
                    "description": "Telex webhook URL for receiving notifications",
                    "required": True,
                    "default": ""
                },
                {
                    "label": "inactivity_threshold",
                    "type": "number",
                    "description": "Minutes of inactivity before sending alert",
                    "required": False,
                    "default": "15"
                },
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "* * * * *",
                },
            ],
            "tick_url": "{app_url}/tick",
            "target_url": ""
        }
    }
    return integration_settings
