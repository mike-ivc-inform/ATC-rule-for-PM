from pyomo.environ import *

# Create a ConcreteModel
model = ConcreteModel()

# Set of repair teams and maintenance activities
n = 3  # Number of repair teams
m = 5  # Number of maintenance activities

# Define the index sets
model.REPAIR_TEAMS = RangeSet(1, n)
model.ACTIVITIES = RangeSet(1, m)

# Define example data: maintenance activity completion times, deadlines, team capacities, and weights
ci_values = {1: 2, 2: 3, 3: 4, 4: 2, 5: 3}
di_values = {1: 10, 2: 15, 3: 20, 4: 10, 5: 15}
Tj_values = {1: 5, 2: 6, 3: 7}
priority_values = {1: 1, 2: 3, 3: 1, 4: 2, 5: 2}  # Priority values

# Adjust the weights based on priority values
wij_values = {(i, j): priority_values[i] for i in range(1, m+1) for j in range(1, n+1)} 

# Decision variables
model.x = Var(model.ACTIVITIES, model.REPAIR_TEAMS, within=Binary)
model.U = Var(model.ACTIVITIES, model.REPAIR_TEAMS, within=Binary)

# Objective function
model.obj = Objective(expr=sum(wij_values[i, j] * model.x[i, j] for i in model.ACTIVITIES for j in model.REPAIR_TEAMS), sense=maximize)

# Constraints
model.assign_one_activity = ConstraintList()
for i in model.ACTIVITIES:
    model.assign_one_activity.add(sum(model.x[i, j] for j in model.REPAIR_TEAMS) == 1)

model.capacity_constraint = ConstraintList()
for j in model.REPAIR_TEAMS:
    model.capacity_constraint.add(sum(ci_values[i] * model.x[i, j] for i in model.ACTIVITIES) <= Tj_values[j])

model.time_constraint = ConstraintList()
M = 1000  # Large constant
for i in model.ACTIVITIES:
    for j in model.REPAIR_TEAMS:
        model.time_constraint.add(sum(ci_values[i] * model.x[i, j] for i in model.ACTIVITIES) <= di_values[i] + M * (1 - model.U[i, j]))

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
