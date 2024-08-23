### Battery Scheduling Endpoint

**Endpoint**: `/schedule_battery`  
**Method**: `POST`

#### Description

This endpoint schedules battery charging and discharging to minimize costs based on price signals and constraints.

#### Request Payload

- `prices`: Dictionary containing lists of price signals for charging/discharging.
- `soc_start`: Initial state of charge.
- `soc_max`: Maximum state of charge (soft limit).
- `soc_min`: Minimum state of charge.
- `soc_target`: Target state of charge (can be set up to 100% of storage capacity).
- `power_capacity`: Maximum power capacity for charging/discharging.
- `conversion_efficiency`: Efficiency of battery charging/discharging (default is 1).
- `top_up`: Boolean flag to enable topping up to full storage capacity (100%).

#### Response

- `costs`: Total cost incurred for the schedule.
- `power_schedule`: List of power values indicating charging/discharging at each time step.
- `soc_schedule`: List showing the state of charge at each time step.

#### Feature Notes

- The `soc_max` parameter now acts as a soft constraint, meaning that the battery will try to stay below this value most of the time to minimize degradation.
- When `top_up` is enabled, the battery can be charged up to its full storage capacity (100 kWh) as needed, especially towards the end of the scheduling period.
- The optimization model ensures the final state of charge (`soc_target`) is achieved, balancing operational costs and battery health.
