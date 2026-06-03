# app/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from .engine import generate_natal_chart

router = APIRouter()

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    timezone: float = 5.5   # default IST

class ChartResponse(BaseModel):
    ayanamsha: float
    chart: Dict[str, Any]

@router.post("/calculate-chart", response_model=ChartResponse)
async def calculate_chart(data: BirthData):
    try:
        # convert hour to 24‑hour decimal
        hour_decimal = data.hour + data.minute / 60.0
        ayanamsha, chart = generate_natal_chart(
            year=data.year,
            month=data.month,
            day=data.day,
            hour_24=hour_decimal,
            minute=0,   # minute already accounted in hour_decimal
            lat=data.latitude,
            lon=data.longitude,
            timezone_hours=data.timezone
        )
        return ChartResponse(ayanamsha=ayanamsha, chart=chart)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
