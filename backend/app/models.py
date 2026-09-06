from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GenerateRequest(BaseModel):
    links: List[str]

class ScriptRecord(BaseModel):
    id: str
    title: str
    type: str
    links: List[str]
    output: str
    created_at: datetime
    status: str

class ScriptResponse(BaseModel):
    id: str
    title: str
    type: str
    links: List[str]
    output: str
    created_at: str
    status: str

class HistoryResponse(BaseModel):
    items: List[ScriptResponse]
    total: int

class SettingsModel(BaseModel):
    api_base_url: str
    api_key: str
    prompt_template: str = "default"

class ProgressEvent(BaseModel):
    type: str
    index: Optional[int] = None
    status: Optional[str] = None
    message: Optional[str] = None
    records: Optional[List[dict]] = None
