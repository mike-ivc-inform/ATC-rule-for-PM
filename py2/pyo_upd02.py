from pyomo.environ import *

def solve_milp(n, m, T, c, d, w, M):
    model = ConcreteModel()

    # Sets
    model.i = RangeSet(1, m)
    model.j = RangeSet(1, n)

    # Binary decision variables
    model.U = Var(model.i, model.j, within=Binary)

    # Objective function
    model.obj = Objective(expr=sum(w[i] * model.U[i, j] for i in model.i for j in model.j), sense=maximize)

    # Workload constraint
    model.workload_constraint = ConstraintList()
    for j in model.j:
        model.workload_constraint.add(sum(c[i, j] * model.U[i, j] for i in model.i) <= T[j])

    # Deadline constraint
    model.deadline_constraint = ConstraintList()
    for i in model.i:
        model.deadline_constraint.add(d[i] - sum(c[i, j] * model.U[i, j] for j in model.j) >= 0)

    # Assignment constraint
    model.assignment_constraint = ConstraintList()
    for i in model.i:
        model.assignment_constraint.add(sum(model.U[i, j] for j in model.j) == 1)

    # Adjusting deadline constraint
    model.adjusting_deadline_constraint = ConstraintList()
    for i in model.i:
        for j in model.j:
            model.adjusting_deadline_constraint.add(d[i] <= (d[i] + M) * (1 - model.U[i, j]))

    # Solve the model
    solver = SolverFactory('glpk')
    solver.solve(model)

    # Print decision variable values
    print("Decision Variable Values:")
    for i in model.i:
        for j in model.j:
            print(f"U[{i},{j}] = {model.U[i, j].value}")

    # Extract results
    assignment = {}
    for i in model.i:
        for j in model.j:
            if model.U[i, j].value == 1:
                assignment[i] = j
                break

    return assignment

# Example data
n = 3  # Number of repair teams
m = 5  # Number of repair jobs
T = {1: 10, 2: 8, 3: 12}  # Productivity of repair teams
c = {(1, 1): 2, (2, 1): 3, (3, 1): 4, (4, 1): 1, (5, 1): 2,
     (1, 2): 1, (2, 2): 2, (3, 2): 3, (4, 2): 2, (5, 2): 1,
     (1, 3): 3, (2, 3): 1, (3, 3): 2, (4, 3): 1, (5, 3): 3}  # Duration of repair jobs for each team
d = {1: 10, 2: 15, 3: 20, 4: 25, 5: 30}  # Deadlines for repair jobs
w = {1: 3, 2: 1, 3: 2, 4: 4, 5: 2}  # Priority values for repair jobs
M = 5  # Maximum amount by which the deadline can be increased

# Solve the MILP problem
assignment = solve_milp(n, m, T, c, d, w, M)

# Print the assignment
print("Assignment:")
for i, j in assignment.items():
    print(f"Job {i} assigned to Repair Team {j}")
