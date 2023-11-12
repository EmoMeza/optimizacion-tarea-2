import pulp
import itertools
import time


def read_atsp_data(file_path):


    distances = {}
    start_reading = False
    city_index = 0

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if "EDGE_WEIGHT_SECTION" in line:
                start_reading = True
                continue
            if start_reading:
                if "EOF" in line or not line:
                    break
                values = line.split()
                for j, value in enumerate(values):
                    value = int(value)
                    if value != 9999:  # Skip the '9999' values
                        distances[(city_index, j)] = value
                city_index += 1

    return distances

def solve_atsp_model(model_name, distances, num_colonies):
    problem = pulp.LpProblem(f"Interstellar_ATSP_{model_name}", pulp.LpMinimize)
    

    # Common decision variable for all models
    x = pulp.LpVariable.dicts("x", distances, cat='Binary')

    # Objective function
    problem += pulp.lpSum(distances[i, j] * x[i, j] for (i, j) in distances)

    # Common DFJ Constraints for all models
    for i in range(num_colonies):
        problem += pulp.lpSum(x[(i, j)] for j in range(num_colonies) if (i, j) in x) == 1
        problem += pulp.lpSum(x[(j, i)] for j in range(num_colonies) if (j, i) in x) == 1

    if model_name == "DFJ":
        # Subtour elimination constraints for DFJ
        for S in range(2, num_colonies):
            for subset in itertools.combinations(range(num_colonies), S):
                problem += pulp.lpSum(x[(i, j)] for i in subset for j in subset if i != j and (i, j) in x) <= len(subset) - 1

    # MTZ Model Adjustments
    if model_name == "MTZ":
        u = pulp.LpVariable.dicts("u", list(range(num_colonies)), lowBound=1, upBound=num_colonies-1, cat='Continuous')
        for i in range(1, num_colonies):
            for j in range(1, num_colonies):
                if i != j and (i, j) in x:
                    problem += u[i] - u[j] + (num_colonies - 1) * x[(i, j)] <= num_colonies - 2


    # GG Model Adjustments
    if model_name == "GG":
        # Assuming '0' is the base
        g = pulp.LpVariable.dicts("g", ((i, j) for i in range(num_colonies) for j in range(num_colonies) if (i, j) in x), lowBound=0, cat='Integer')

        # Flow conservation constraints
        for i in range(num_colonies):
            if i == 0:  # Base node
                problem += pulp.lpSum(g[(i, j)] for j in range(num_colonies) if (i, j) in g) == 1  # One unit leaves the base
                problem += pulp.lpSum(g[(j, i)] for j in range(num_colonies) if (j, i) in g) == 1  # One unit returns to the base
            else:
                problem += pulp.lpSum(g[(i, j)] for j in range(num_colonies) if (i, j) in g) - pulp.lpSum(g[(j, i)] for j in range(num_colonies) if (j, i) in g) == 0  # Flow conservation

        # Linking flow variables to decision variables
        for i, j in g:
            problem += g[(i, j)] <= (num_colonies - 1) * x[(i, j)]


    # Set solver output to False
    pulp.LpSolverDefault.msg = False

    # Solve the problem
    start_time = time.time()
    # problem.solve()
    problem.solve()  # Sets a relative gap tolerance of 1%
    end_time = time.time()

    
    # Output results
    print(f"Model: {model_name}")
    print("Status:", pulp.LpStatus[problem.status])
    print("Total Distance:", pulp.value(problem.objective))
    print("Computation Time:", end_time - start_time, "seconds")
    print()

# Main execution
# filename = 'Data/random_atsp_instance2.atsp'
filename = 'Data/br17.atsp'
distances = read_atsp_data(filename)
num_colonies = max(max(i, j) for i, j in distances) + 1

# Solve each model
# for model in ["DFJ", "MTZ", "GG"]:
# for model in ["MTZ", "GG"]:
for model in ["GG"]:
    solve_atsp_model(model, distances, num_colonies)
