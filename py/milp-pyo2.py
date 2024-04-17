from pyomo.environ import *

# Create a ConcreteModel
model = ConcreteModel()

# Set of repair teams and maintenance activities
n = 3  # Number of repair teams
m = 5  # Number of maintenance activities

# Define the index sets
model.REPAIR_TEAMS = RangeSet(1, n)
model.ACTIVITIES = RangeSet(1, m)

# Decision variables
model.x = Var(model.ACTIVITIES, model.REPAIR_TEAMS, within=Binary)
model.U = Var(model.ACTIVITIES, model.REPAIR_TEAMS, within=Binary)

# Objective function
model.obj = Objective(expr=sum(wij * model.x[i, j] for i in model.ACTIVITIES for j in model.REPAIR_TEAMS), sense=maximize)

# Constraints
model.assign_one_activity = ConstraintList()
for i in model.ACTIVITIES:
    model.assign_one_activity.add(sum(model.x[i, j] for j in model.REPAIR_TEAMS) == 1)

model.capacity_constraint = ConstraintList()
for j in model.REPAIR_TEAMS:
    model.capacity_constraint.add(sum(ci * model.x[i, j] for i in model.ACTIVITIES) <= Tj)

model.time_constraint = ConstraintList()
M = 1000  # Large constant
for i in model.ACTIVITIES:
    for j in model.REPAIR_TEAMS:
        model.time_constraint.add(sum(ci * model.x[i, j] for i in model.ACTIVITIES) <= di + M * (1 - model.U[i, j]))

# Solve the MILP
solver = SolverFactory('glpk')
results = solver.solve(model)

# Print results
print("Optimal solution:")
for i in model.ACTIVITIES:
    for j in model.REPAIR_TEAMS:
        if model.x[i, j].value == 1:
            print(f"Assign activity {i} to repair team {j}")

print("Total weighted completion time:", model.obj())
