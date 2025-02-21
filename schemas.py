from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional


monitor_state: Dict[str, dict] = {}


class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str

class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]


    def get_setting(self, label: str) -> Optional[str]:
        for setting in self.settings:
            if setting.label == label:
                return setting.default
        return None


class MonitoringStatus(BaseModel):
    app_url: str
    last_active: datetime
    is_active: bool
    current_status: str
