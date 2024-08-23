from pyomo.environ import ConcreteModel, Var, Objective, Constraint, NonNegativeReals, SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition
from fastapi import HTTPException

def solve_battery_schedule(params, top_up):
    model = ConcreteModel()

    # Number of time steps
    T = 6
    model.T = range(T)

    # Parameters
    model.soc_start = params.soc_start
    model.soc_min = params.soc_min
    model.soc_max = params.soc_max
    model.soc_target = params.soc_target
    model.power_capacity = params.power_capacity
    model.conversion_efficiency = params.conversion_efficiency
    model.storage_capacity = params.storage_capacity

    # Variables
    model.charge = Var(model.T, domain=NonNegativeReals)
    model.discharge = Var(model.T, domain=NonNegativeReals)
    model.soc = Var(model.T, domain=NonNegativeReals)

    # Objective
    def objective_rule(model):
        return sum(
            (0.1 * model.charge[t] - 0.1 * model.discharge[t])
            for t in model.T
        )
    model.obj = Objective(rule=objective_rule)

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
    solver = SolverFactory('glpk')
    results = solver.solve(model)

    if results.solver.status != SolverStatus.ok or results.solver.termination_condition != TerminationCondition.optimal:
        raise HTTPException(status_code=400, detail="Infeasible problem or no solution found")

    schedule = {
        "total_cost": model.obj(),
        "charge_schedule": [model.charge[t].value for t in model.T],
        "discharge_schedule": [model.discharge[t].value for t in model.T],
        "soc_schedule": [model.soc[t].value for t in model.T]
    }
    return schedule
