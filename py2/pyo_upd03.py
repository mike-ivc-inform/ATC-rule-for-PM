from pyomo.environ import *

# Create a Concrete Model
model = ConcreteModel()

# Sets
model.I = Set(initialize=[1, 2, 3])  # Set of repair jobs
model.J = Set(initialize=[1, 2])     # Set of repair teams

# Parameters
# Example data, replace with your actual data
model.d = Param(model.I, initialize={1: 5, 2: 8, 3: 10})  # Planned period for each job
model.c = Param(model.I, initialize={1: 2, 2: 3, 3: 4})   # Standard duration for each job
model.w = Param(model.I, initialize={1: 2, 2: 3, 3: 1})   # Priority value for each job
model.T = Param(model.J, initialize={1: 6, 2: 5})         # Productivity of each repair team
M = 100  # Penalty for not completing work on time

# Binary variables
model.x = Var(model.I, model.J, within=Binary)  # Assignment of jobs to repair teams
model.z = Var(model.I, within=Binary)           # Completion of jobs on time
model.U = Var(model.I, model.J, within=Binary)  # Binary variable for ability to complete work on time

# Objective function
def obj_rule(model):
    return sum(model.w[i] * model.z[i] for i in model.I)
model.obj = Objective(rule=obj_rule, sense=maximize)

# Constraints
# Each job is assigned to exactly one repair team
def assign_rule(model, i):
    return sum(model.x[i, j] for j in model.J) == 1
model.assign_constraint = Constraint(model.I, rule=assign_rule)

# Workload constraint for each repair team
def workload_rule(model, j):
    return sum(model.c[i] * model.x[i, j] for i in model.I) <= model.T[j]
model.workload_constraint = Constraint(model.J, rule=workload_rule)

# Binary variable U constraints
def U_constraint_rule(model, i, j):
    return model.U[i, j] <= model.x[i, j]
model.U_constraint = Constraint(model.I, model.J, rule=U_constraint_rule)

def U_penalty_rule(model, i, j):
    return model.U[i, j] * (model.d[i] + M) >= model.d[i] * model.x[i, j]
model.U_penalty_constraint = Constraint(model.I, model.J, rule=U_penalty_rule)

# Constraint for completing work on time
def on_time_rule(model, i, j):
    return model.z[i] <= 1 - model.U[i, j]
model.on_time_constraint = Constraint(model.I, model.J, rule=on_time_rule)

# Solve the model
solver = SolverFactory('glpk')
results = solver.solve(model)

# Print results
print("Objective Value:", value(model.obj))

print("\nAssignment of Jobs to Repair Teams:")
for i in model.I:
    for j in model.J:
        if value(model.x[i, j]) == 1:
            print(f"Job {i} assigned to Repair Team {j}")

print("\nCompletion of Jobs on Time:")
for i in model.I:
    print(f"Job {i}: {value(model.z[i])}")

print("\nBinary Variable U (Ability to Complete Work on Time):")
for i in model.I:
    for j in model.J:
        print(f"Job {i}, Repair Team {j}: {value(model.U[i, j])}")
