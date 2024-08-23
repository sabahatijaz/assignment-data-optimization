from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from schedule import solve_battery_schedule

app = FastAPI()

class ScheduleParameters(BaseModel):
    soc_start: float
    soc_min: float
    soc_max: float
    soc_target: float
    power_capacity: float
    conversion_efficiency: float
    storage_capacity: float

@app.get("/schedule")
def get_schedule(
    soc_start: float,
    soc_min: float,
    soc_max: float,
    soc_target: float,
    power_capacity: float,
    conversion_efficiency: float,
    storage_capacity: float,
    top_up: bool = Query(False)
):
    params = ScheduleParameters(
        soc_start=soc_start,
        soc_min=soc_min,
        soc_max=soc_max,
        soc_target=soc_target,
        power_capacity=power_capacity,
        conversion_efficiency=conversion_efficiency,
        storage_capacity=storage_capacity
    )
    try:
        return solve_battery_schedule(params, top_up)
    except HTTPException as e:
        raise e
