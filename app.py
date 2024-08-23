from fastapi import FastAPI, HTTPException, Query
from typing_extensions import Annotated
from pydantic import BaseModel, field_validator,ValidationInfo
from typing import Optional, Dict, Any, List
import pandas as pd
from schedule import solve_battery_schedule

app = FastAPI()

class ScheduleParameters(BaseModel):
    soc_start: float
    soc_max: float
    soc_min: float
    soc_target: float
    power_capacity: float
    conversion_efficiency: float
    storage_capacity: float
    prices: Dict[str, Any]  # Dict to handle the prices input

    @field_validator('soc_min', 'soc_max')
    @classmethod
    def check_soc_values(cls, v: float, info: ValidationInfo) -> float:
        if 'soc_min' in info.field_name and v > info.data['soc_max']:
            raise ValueError('soc_min must not be greater than soc_max')
        return v

    @field_validator('prices')
    @classmethod
    def validate_prices(cls, v: Dict[str, Any], info: ValidationInfo) -> Dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError('prices must be a dictionary')
        if 'production' not in v or 'consumption' not in v:
            raise ValueError('Prices must contain "production" and "consumption" keys')
        if len(v['production']) != len(v['consumption']):
            raise ValueError('Length of production and consumption must be the same')
        return value
        return v


class BatteryScheduleResponse(BaseModel):
    total_cost: float
    charge_schedule: List[float]
    discharge_schedule: List[float]
    soc_schedule: List[float]

@app.post("/schedule")
def get_schedule(params: ScheduleParameters, top_up: bool = Query(False)):
    prices_df = pd.DataFrame(params.prices)
    try:
        result = solve_battery_schedule(
            prices_df=prices_df,
            soc_start=params.soc_start,
            soc_max=params.soc_max,
            soc_min=params.soc_min,
            soc_target=params.soc_target,
            power_capacity=params.power_capacity,
            conversion_efficiency=params.conversion_efficiency
        )
        return BatteryScheduleResponse(
            total_cost=result["total_cost"],
            charge_schedule=result["charge_schedule"],
            discharge_schedule=result["discharge_schedule"],
            soc_schedule=result["soc_schedule"]
        )
    except HTTPException as e:
        raise e
