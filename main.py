from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from schemas import MonitoringStatus, monitor_state, MonitorPayload
from render_monitor import monitor_app  
from typing import List
import logging


app = FastAPI(
    title="Render Monitor", 
    description="Monitor Render apps for inactivity"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://staging.telextest.im", 
        "http://telextest.im", 
        "https://staging.telex.im", 
        "https://telex.im",
        "https://render-monitor-kk3h.onrender.com"
    ], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @app.post("/monitor/start")
@app.post("/tick")
async def start_monitoring(payload: MonitorPayload, background_tasks: BackgroundTasks):
    logger.info(f"Received payload: {payload}")
    
    background_tasks.add_task(monitor_app, payload)
    
    logger.info("Background task added successfully")
    
    return {"status": "accepted"}


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
async def get_json_settings(request: Request):
    base_url = str(request.base_url).rstrip("/")
    
    return {
        "data": {
            "date": {
                "created_at": "2025-02-19",
                "updated_at": "2025-02-19"
            },
            "descriptions": {
                "app_description": "Monitor your Render apps for inactivity and receive alerts when they go to sleep.",
                "app_logo": "https://img.freepik.com/fotos-premium/ilustracao-de-renderizacao-3d-on-line-de-rastreamento-de-entrega_7209-806.jpg?w=996",
                "app_name": "Render Monitor",
                "app_url": base_url,
                "background_color": "#4A90E2"
            },
            "integration_category": "Monitoring & Logging",
            "integration_type": "interval",
            "is_active": False,
            "key_features": [
                "Monitor Render apps for inactivity",
                "Configurable inactivity threshold",
                "Instant inactivity notifications"
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
                    "label": "inactivity_threshold",
                    "type": "number",
                    "description": "Minutes of inactivity before sending alert",
                    "required": False,
                    "default": "15"
                },
                {
                    "label": "interval",
                    "type": "text",
                    "description": "Monitoring check interval (cron format)",
                    "required": True,
                    "default": "*/15 * * * *"
                }
            ],
            "tick_url": f"{base_url}/tick",
            "target_url": ""
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)