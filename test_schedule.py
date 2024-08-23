import pandas as pd
import pytest
from schedule import solve_battery_schedule

def test_solve_battery_schedule():
    # Sample input
    prices = pd.DataFrame({
        'production': [7, 2, 3, 4, 1, 6],
        'consumption': [8, 3, 4, 5, 2, 7]
    })

    soc_start = 10
    soc_max = 90
    soc_min = 10
    soc_target = 90
    power_capacity = 10
    conversion_efficiency = 1.0

    # Expected output structure
    expected_keys = {"total_cost", "charge_schedule", "discharge_schedule", "soc_schedule"}

    result = solve_battery_schedule(
        prices_df=prices,
        soc_start=soc_start,
        soc_max=soc_max,
        soc_min=soc_min,
        soc_target=soc_target,
        power_capacity=power_capacity,
        conversion_efficiency=conversion_efficiency
    )

    # Check if the result contains all expected keys
    assert isinstance(result, dict)
    assert expected_keys.issubset(result.keys())
    assert isinstance(result["total_cost"], (int, float))
    assert all(isinstance(x, (int, float)) for x in result["charge_schedule"])
    assert all(isinstance(x, (int, float)) for x in result["discharge_schedule"])
    assert all(isinstance(x, (int, float)) for x in result["soc_schedule"])
