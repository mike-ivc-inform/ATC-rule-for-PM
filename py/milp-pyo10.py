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

# Create a Pyomo Concrete Model
model = ConcreteModel()

# Define binary decision variables
model.x = Var(range(1, m + 1), range(1, n + 1), domain=Binary)
model.V = Var(range(1, m + 1), range(1, n + 1), domain=Binary)

# Define objective function
model.obj = Objective(expr=sum(w[i, j] * model.V[i, j] for i in range(1, m + 1) for j in range(1, n + 1)),
                      sense=maximize)

# Define constraints
model.constraints = ConstraintList()
for i in range(1, m + 1):
    model.constraints.add(sum(model.x[i, j] for j in range(1, n + 1)) == 1)

for j in range(1, n + 1):
    model.constraints.add(sum(c[i] * model.x[i, j] for i in range(1, m + 1)) <= T[j])

for i in range(1, m + 1):
    for j in range(1, n + 1):
        model.constraints.add(model.x[i, j] <= model.V[i, j])

# Solve the optimization problem
solver = SolverFactory('glpk')
solver.solve(model)

# Print the results
print("Optimal Solution:")
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if value(model.x[i, j]) == 1:
            print(f"Job {i} is assigned to repair team {j}.")
            if value(model.V[i, j]) == 1:
                print("  Job completed on time.")
            else:
                print("  Job completed late.")

#---------------------2-------------------------------
# Identify late work from Iteration 1
late_work = [(i, j) for i in range(1, m + 1) for j in range(1, n + 1) if value(model.x[i, j]) == 0]

# Print late work identified
print("Late Work Identified (Iteration 2):")
for work in late_work:
    print(f"Job {work[0]} was not assigned to any team.")

#---------------------3-----------------------------------
# Create a Pyomo Concrete Model for Iteration 3
model_iter3 = ConcreteModel()

# Define binary decision variables
model_iter3.x = Var(range(1, m + 1), range(1, n + 1), domain=Binary)
model_iter3.L = Var(range(1, m + 1), range(1, n + 1), domain=Binary)

# Define objective function
model_iter3.obj = Objective(expr=sum(w[i, j] * model_iter3.L[i, j] for (i, j) in late_work),
                            sense=maximize)

# Define constraints
model_iter3.constraints = ConstraintList()
for i in range(1, m + 1):
    for j in range(1, n + 1):
        model_iter3.constraints.add(model_iter3.x[i, j] + model_iter3.L[i, j] == 1)

# Solve the optimization problem for Iteration 3
solver.solve(model_iter3)

# Print the results of Iteration 3
print("Optimal Solution for Iteration 3:")
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if value(model_iter3.x[i, j]) == 1:
            print(f"Job {i} is assigned to repair team {j}.")
            if value(model_iter3.L[i, j]) == 1:
                print("  Job completed late.")

