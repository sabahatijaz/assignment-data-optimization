import pandas as pd
from pyomo.environ import ConcreteModel, Var, Objective, Constraint, NonNegativeReals, SolverFactory, minimize
from pyomo.opt import SolverStatus, TerminationCondition
from fastapi import HTTPException

def solve_battery_schedule(prices_df: pd.DataFrame,
    soc_start: float,
    soc_max: float,
    soc_min: float,
    soc_target: float,
    power_capacity: float,
    conversion_efficiency: float = 1.0,top_up=False,storage_capacity=100,penalty_per_unit=1):
    model = ConcreteModel()

    # Number of time steps
    T = len(prices_df)
    model.T = range(T)

    # Parameters
    model.soc_start = soc_start
    model.soc_min = soc_min
    model.soc_max = soc_max
    model.soc_target = soc_target
    model.power_capacity = power_capacity
    model.conversion_efficiency = conversion_efficiency
    model.storage_capacity = storage_capacity
    model.penalty_per_unit = penalty_per_unit
    
    # Prices
    model.price_consumption= [prices_df['consumption'][t] for t in model.T]
    model.price_production = [prices_df['production'][t] for t in model.T]

    # Variables
    model.charge = Var(model.T, domain=NonNegativeReals)
    model.discharge = Var(model.T, domain=NonNegativeReals)
    model.soc = Var(model.T, domain=NonNegativeReals)

    # Objective
    def cost_function(model):
        cost = sum(
            (model.price_consumption[t] * model.charge[t] - model.price_production[t] * model.discharge[t])
            for t in model.T
        )
        penalty = sum(
            model.penalty_per_unit * (model.soc[t] - model.soc_max)
            for t in model.T if model.soc[t] > model.soc_max
        )
        return cost + penalty
    
    model.costs = Objective(rule=cost_function, sense=minimize)

    # Constraints
    def soc_constraint_rule(model, t):
        if t == 0:
            return model.soc[t] == model.soc_start + (model.conversion_efficiency * model.charge[t] - model.discharge[t] / model.conversion_efficiency)
        else:
            return model.soc[t] == model.soc[t - 1] + (model.conversion_efficiency * model.charge[t] - model.discharge[t] / model.conversion_efficiency)
    model.soc_constraint = Constraint(model.T, rule=soc_constraint_rule)

    def soc_bounds_rule(model, t):
        return (model.soc_min, model.soc[t], model.soc_max)
    model.soc_bounds = Constraint(model.T, rule=soc_bounds_rule)

    def charge_bounds_rule(model, t):
        return (0, model.charge[t], model.power_capacity)
    model.charge_bounds = Constraint(model.T, rule=charge_bounds_rule)

    def discharge_bounds_rule(model, t):
        return (0, model.discharge[t], model.power_capacity)
    model.discharge_bounds = Constraint(model.T, rule=discharge_bounds_rule)

    if top_up:
        def target_constraint_rule(model):
            return model.soc[T - 1] == model.storage_capacity
        model.target_constraint = Constraint(rule=target_constraint_rule)
        
        def soc_soft_constraint_rule(model, t):
            if t == T - 1:
                return model.soc[t] <= model.soc_max + (model.storage_capacity - model.soc_max) * 0.1
            return model.soc_min <= model.soc[t] <= model.soc_max
        model.soc_soft_constraint = Constraint(model.T, rule=soc_soft_constraint_rule)

    # Solve the model
    solver = SolverFactory('appsi_highs')
    try:
        results = solver.solve(model, tee=True)
        if results.solver.status != SolverStatus.ok:
            raise HTTPException(status_code=400, detail="Solver did not return an OK status.")
        if results.solver.termination_condition != TerminationCondition.optimal:
            raise HTTPException(status_code=400, detail="Solver did not find an optimal solution.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while solving the model: {str(e)}")

    # Extract and return results
    try:
        schedule = {
            "total_cost": model.costs(),
            "charge_schedule": [model.charge[t].value for t in model.T],
            "discharge_schedule": [model.discharge[t].value for t in model.T],
            "soc_schedule": [model.soc[t].value for t in model.T]
        }
    except AttributeError as e:
        raise HTTPException(status_code=500, detail=f"Error extracting results: {str(e)}")

    return schedule
