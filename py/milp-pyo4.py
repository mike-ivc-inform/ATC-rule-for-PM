from pyomo.environ import *

# Define parameters
n = 5
m = 43
c = [3.0, 4.0, 4.0, 3.9, 3.1, 3.9, 2.7, 4.0, 3.1, 7.9, 5.9, 3.8, 3.1, 2.0, 7.8, 3.1, 3.3, 2.0, 3.0, 4.1, 7.8, 2.9, 5.1, 2.0, 3.0, 4.8, 2.1, 4.0, 6.0, 3.1, 4.0, 3.2, 2.0, 4.0, 4.9, 2.2, 2.1, 3.0, 2.1, 2.0, 3.0, 2.1, 1.9]
d = [5, 6, 6, 6, 8, 7, 8, 10, 9, 13, 3, 8, 11, 11, 16, 12, 13, 12, 15, 16, 21, 16, 5, 17, 18, 20, 20, 22, 24, 21, 23, 22, 22, 24, 25, 25, 25, 26, 25, 27, 29, 29, 29]
w = [1.2, 1.2, 3.9, 1.0, 3.7, 1.4, 2.1, 1.9, 1.4, 1.5, 4.1, 1.5, 1.4, 1.3, 2.1, 2.0, 1.7, 1.1, 1.0, 1.5, 2.1, 4.0, 2.2, 3.8, 1.6, 2.0, 4.0, 3.3, 3.0, 2.4, 3.9, 2.0, 4.0, 2.2, 3.3, 1.7, 1.8, 2.1, 2.9, 3.7, 2.7, 2.8, 2.9]
T = 22

# Create a Concrete Model
model = ConcreteModel()

# Define the decision variables
model.x = Var(range(1, m+1), range(1, n+1), within=Binary)
model.U = Var(range(1, m+1), range(1, n+1), within=Binary)

# Define the objective function
model.obj = Objective(expr=sum(w[i-1] * model.U[i, j] for i in range(1, m+1) for j in range(1, n+1)), sense=maximize)

# Define constraints
def maintenance_team_constraint(model, i):
    return sum(model.x[i, j] for j in range(1, n+1)) == 1
model.maintenance_team_constraint = Constraint(range(1, m+1), rule=maintenance_team_constraint)

def productivity_constraint(model, j):
    return sum(c[i-1] * model.x[i, j] for i in range(1, m+1)) <= T
model.productivity_constraint = Constraint(range(1, n+1), rule=productivity_constraint)

def time_limit_constraint(model, i, j):
    return sum(c[i-1] * model.x[i, j] for i in range(1, m+1)) <= d[i-1] + 1000 * (1 - model.U[i, j])  # 1000 is assumed to be a large constant
model.time_limit_constraint = Constraint(range(1, m+1), range(1, n+1), rule=time_limit_constraint)

# Solve the optimization problem
solver = SolverFactory('glpk')  # Use any solver of your choice, here GLPK is used
results = solver.solve(model)

# Print the results
print("Optimal Solution:")
for i in range(1, m+1):
    for j in range(1, n+1):
        if model.x[i, j].value == 1:
            print(f"Job {i} assigned to team {j}")
