from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Dict


monitor_state: Dict[str, dict] = {}

class App(BaseModel):
    app_url: HttpUrl
    webhook_url: HttpUrl
    inactivity_threshold: int = 15


class MonitoringStatus(BaseModel):
    app_url: str
    last_active: datetime
    is_active: bool
    current_status: str
