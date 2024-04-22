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

# Calculate total complexity of all jobs
total_complexity = sum(c[i] for i in range(1, m + 1))

# Check if total complexity exceeds total productivity
if total_complexity > sum(T.values()):
    # Identify the job with lowest priority and longest deadline
    excluded_job = min(w, key=lambda k: (w[k], -d[k]))
    print(f"Excluded job: {excluded_job}")

    # Remove the excluded job from the list of jobs
    m -= 1
    del c[excluded_job[0]]
    del d[excluded_job[0]]
    del w[excluded_job]

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

# Print the results of the first iteration
print("First Iteration - Works included in calculation:")
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if value(model.x[i, j]) == 1:
            print(f"Job {i} is assigned to repair team {j}.")

# Identify late work from Iteration 1
included_work = [(i, j) for i in range(1, m + 1) for j in range(1, n + 1) if value(model.x[i, j]) == 1]
excluded_work = [(i, j) for i in range(1, m + 1) for j in range(1, n + 1) if value(model.x[i, j]) == 0]

# Print works for third iteration
print("\nThird Iteration - Works excluded from the calculation:")
for work in excluded_work:
    print(f"Job {work[0]} was not assigned to any team.")
