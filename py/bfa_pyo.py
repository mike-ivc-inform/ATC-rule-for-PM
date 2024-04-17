from pyomo.environ import *

# Create a ConcreteModel
model = ConcreteModel()

# Set of repair teams and maintenance activities
repair_teams = ['Team1', 'Team2', 'Team3']
maintenance_activities = ['Activity1', 'Activity2', 'Activity3']

# Decision variables
model.x = Var(maintenance_activities, repair_teams, within=Binary)
model.completion_time = Var(maintenance_activities, within=NonNegativeReals)

# Objective function
model.obj = Objective(expr=sum(model.completion_time[activity] for activity in maintenance_activities), sense=minimize)

# Constraints
model.assign_one_activity = ConstraintList()
for activity in maintenance_activities:
    model.assign_one_activity.add(sum(model.x[activity, team] for team in repair_teams) == 1)

# Capacity constraints
team_capacity = {'Team1': 2, 'Team2': 3, 'Team3': 2}
model.capacity_constraint = ConstraintList()
for team in repair_teams:
    model.capacity_constraint.add(sum(model.x[activity, team] for activity in maintenance_activities) <= team_capacity[team])

# Solve the MILP
solver = SolverFactory('glpk')
results = solver.solve(model)

# Print results
print("Optimal solution:")
for activity in maintenance_activities:
    for team in repair_teams:
        if model.x[activity, team].value == 1:
            print(f"Assign {activity} to {team}")

print("Total completion time:", model.obj())
