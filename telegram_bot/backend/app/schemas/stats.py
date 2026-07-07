from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StatsResponse(BaseModel):
    total_users: int = 0
    active_users_7d: int = 0
    today_messages: int = 0
    cpu_usage: float = 0.0
    ram_usage: float = 0.0
    error_count: int = 0


class ActivityPoint(BaseModel):
    date: str
    count: int


class CEFRDistribution(BaseModel):
    A1: int = 0
    A2: int = 0
    B1: int = 0
    B2: int = 0
    C1: int = 0
    C2: int = 0