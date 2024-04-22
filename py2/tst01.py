from pyomo.environ import *

# Define the repair teams, jobs, and parameters
n = 3  # number of repair teams
m = 5  # number of maintenance and repair works
c = {1: 3, 2: 2, 3: 4, 4: 5, 5: 2}  # complexity of each job
d = {1: 10, 2: 8, 3: 12, 4: 15, 5: 7}  # completion date of each job
w = {(1, 1): 3, (1, 2): 4, (1, 3): 2,
     (2, 1): 2, (2, 2): 3, (2, 3): 5,
     (3, 1): 4, (3, 2): 3, (3, 3): 2,
     (4, 1): 5, (4, 2): 2, (4, 3): 4,
     (5, 1): 3, (5, 2): 4, (5, 3): 2}
T = {1: 10, 2: 12, 3: 8}  # maximum productivity of each repair team

# Define the model
model = ConcreteModel()

# Sets
model.n = RangeSet(1, n)
model.m = RangeSet(1, m)

# Parameters
model.c = Param(model.m, initialize=c)
model.d = Param(model.m, initialize=d)
model.w = Param(model.m, model.n, initialize=w)
model.T = Param(model.n, initialize=T)

# Decision variables
model.x = Var(model.m, model.n, within=Binary)
model.U = Var(model.m, model.n, within=Binary)

# Objective function
def objective_rule(model):
    return sum(model.w[i, j] * model.U[i, j] for i in model.m for j in model.n)
model.objective = Objective(rule=objective_rule, sense=maximize)

# Constraints
def assignment_rule(model, i):
    return sum(model.x[i, j] for j in model.n) == 1
model.assignment_constraint = Constraint(model.m, rule=assignment_rule)

def workload_rule(model, j):
    return sum(model.c[i] * model.x[i, j] for i in model.m) <= model.T[j]
model.workload_constraint = Constraint(model.n, rule=workload_rule)

def deadline_rule(model, i):
    return sum(model.d[i] * model.U[i, j] for j in model.n) <= model.d[i]
model.deadline_constraint = Constraint(model.m, rule=deadline_rule)

# Solve the model
solver = SolverFactory('glpk')
solver.solve(model)

# Print results
print("Objective value:", model.objective())
print("\nJob assignments:")
for i in model.m:
    for j in model.n:
        if model.x[i, j].value == 1:
            print(f"Job {i} assigned to repair team {j}")
print("\nCompletion status:")
for i in model.m:
    for j in model.n:
        if model.U[i, j].value == 1:
            print(f"Job {i} completed on time by repair team {j}")

#----------------------------------------------------------------
Objective value: 22.0

Job assignments:
Job 1 assigned to repair team 3
Job 2 assigned to repair team 3
Job 3 assigned to repair team 1
Job 4 assigned to repair team 1
Job 5 assigned to repair team 3

Completion status:
Job 1 completed on time by repair team 2
Job 2 completed on time by repair team 3
Job 3 completed on time by repair team 1
Job 4 completed on time by repair team 1
Job 5 completed on time by repair team 2
