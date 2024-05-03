from pyomo.environ import *

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

# Create a Concrete Model
model = ConcreteModel()

# Sets
model.I = RangeSet(1, m)  # Set of repair jobs
model.J = RangeSet(1, n)  # Set of repair teams

# Parameters
model.d = Param(model.I, initialize=d)  # Planned period for each job
model.T = Param(model.J, initialize=T)  # Productivity of repair teams
model.w = Param(model.I, initialize=w)  # Priority values for repair jobs

# Duration of repair jobs parameter is now defined as a dictionary
def c_init(model, i, j):
    return c[i, j]
model.c = Param(model.I, model.J, initialize=c_init)  # Duration of repair jobs for each team

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
    return sum(model.c[i, j] * model.x[i, j] for i in model.I) <= model.T[j]
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

print("\nDeadlines for repair jobs:")
for i in model.I:
    print(f"Deadlin job {i}: {value(model.d[i])}")

print("\nProductivity of repair teams:")
for j in model.J:
    print(f"Productivity teams {j}: {value(model.T[j])}")

print("\nPriority values for repair jobs:")
for i in model.I:
    print(f"Priority jobs {i}: {value(model.w[i])}")

# -------- add Graph ---------------------------------
import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Add nodes for repair teams
for j in model.J:
    G.add_node(f"Team {j}")

# Add edges for assigned jobs
for i in model.I:
    for j in model.J:
        if value(model.x[i, j]) == 1:
            G.add_edge(f"Team {j}", f"Job {i}")

# Plot the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)  # Positions for all nodes
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold", edge_color="gray", arrowsize=20)
plt.title("Assigned Work for Repair Teams", fontsize=15)
plt.show()

# --------- COLORS -------------------------------
import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Add nodes for repair teams
for j in model.J:
    G.add_node(f"Team {j}", color='blue')

# Add nodes for jobs
for i in model.I:
    G.add_node(f"Job {i}", color='green')

# Add edges for assigned jobs
for i in model.I:
    for j in model.J:
        if value(model.x[i, j]) == 1:
            G.add_edge(f"Team {j}", f"Job {i}")

# Plot the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)  # Positions for all nodes

# Draw nodes
node_colors = [G.nodes[node]['color'] for node in G.nodes]
nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors)

# Draw edges
nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=20)

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

# Set title
plt.title("Assigned Work for Repair Teams", fontsize=15)

plt.axis('off')
plt.show()

# --------------icons -----------------
import PIL
# Image URLs for graph nodes
icons = {
    "job": "icons/operation.png",
    "team": "icons/group.png",
}

# Load images
images = {k: PIL.Image.open(fname) for k, fname in icons.items()}
# Add nodes for repair teams
for j in model.J:
    G.add_node(f"Team {j}",  image=images["team"])

# Add nodes for jobs
for i in model.I:
    G.add_node(f"Job {i}",  image=images["job"])

# Add edges for assigned jobs
for i in model.I:
    for j in model.J:
        if value(model.x[i, j]) == 1:
            G.add_edge(f"Team {j}", f"Job {i}")

# --------Изменение кода -----------
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import PIL

# Create a directed graph
G = nx.DiGraph()

# Image URLs for graph nodes
icons = {
    "job": "icons/operation.png",
    "team": "icons/group.png",
}

# Load images
images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

# Add nodes for repair teams
for j in model.J:
    G.add_node(f"Team {j}", image=images["team"])

# Add nodes for jobs
for i in model.I:
    G.add_node(f"Job {i}", image=images["job"])

# Add edges for assigned jobs
for i in model.I:
    for j in model.J:
        if value(model.x[i, j]) == 1:
            G.add_edge(f"Team {j}", f"Job {i}")

# Plot the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)  # Positions for all nodes

# Draw nodes with icons
for node, (x, y) in pos.items():
    if "Team" in node:
        image = images["team"]
    else:
        image = images["job"]
    im = OffsetImage(image, zoom=0.1)
    ab = AnnotationBbox(im, (x, y), xycoords='data', frameon=False)
    plt.gca().add_artist(ab)

# Draw edges
nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=20)

# Set title
plt.title("Assigned Work for Repair Teams", fontsize=15)

plt.axis('off')
plt.show()

# ----------LABLES -----------------
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import PIL

# Create a directed graph
G = nx.DiGraph()

# Image URLs for graph nodes
icons = {
    "job": "icons/operation.png",
    "team": "icons/group.png",
}

# Load images
images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

# Add nodes for repair teams
for j in model.J:
    G.add_node(f"Team {j}", image=images["team"], label=f"Team {j}")

# Add nodes for jobs
for i in model.I:
    G.add_node(f"Job {i}", image=images["job"], label=f"Job {i}")

# Add edges for assigned jobs
for i in model.I:
    for j in model.J:
        if value(model.x[i, j]) == 1:
            G.add_edge(f"Team {j}", f"Job {i}")

# Plot the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)  # Positions for all nodes

# Draw nodes with icons and labels
for node, (x, y) in pos.items():
    if "Team" in node:
        image = images["team"]
    else:
        image = images["job"]
    im = OffsetImage(image, zoom=0.1)
    ab = AnnotationBbox(im, (x, y), xycoords='data', frameon=False)
    plt.gca().add_artist(ab)
    plt.text(x, y - 0.05, G.nodes[node]['label'], ha='center', fontsize=10)

# Draw edges
nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=20)

# Set title
plt.title("Assigned Work for Repair Teams", fontsize=15)

plt.axis('off')
plt.show()
