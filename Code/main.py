import pulp
import itertools
import time
import csv


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
        # Variables representing the order in which each node is visited
        y = pulp.LpVariable.dicts("y", list(range(num_colonies)), lowBound=0, upBound=num_colonies - 1, cat='Continuous')

        # Adding constraints
        for i in range(1, num_colonies):
            for j in range(num_colonies):
                if i != j:
                    problem += y[i] - y[j] + num_colonies * x[(i, j)] <= num_colonies - 1

        # Iterative approach to add GG cuts and solve the problem
        start_time = time.time()
        while True:
            problem.solve()

            # Check if the solution is integer
            if all(x[(i, j)].varValue.is_integer() for (i, j) in x):
                break
            else:
                # Identify a subtour in the non-integer solution
                subtour = [] # This needs a method to find the subtour in the non-integer solution

                # Add a GG cut to eliminate the identified subtour
                problem += pulp.lpSum(x[(i, j)] for (i, j) in subtour) <= len(subtour) - 1
        end_time = time.time()


    # Set solver output to False
    pulp.LpSolverDefault.msg = False

    # Solve the problem
    if model!="GG":
        start_time = time.time()
        problem.solve()
        end_time = time.time()

    
    # Output results
    print(f"Model: {model_name}")
    print("Status:", pulp.LpStatus[problem.status])
    print("Total Distance:", pulp.value(problem.objective))
    print("Computation Time:", end_time - start_time, "seconds")
    print()

    results = {
        "File": filename,  
        "Model": model_name,
        "Status": pulp.LpStatus[problem.status],
        "Total Distance": pulp.value(problem.objective),
        "Computation Time": end_time - start_time
    }
    return results

# Main execution
# Output CSV filename
output_csv = 'atsp_results.csv'

# Initialize results list
results_data = []

# Loop over each file and solve for each model
for i in range(1, 11):  # Assuming you have 10 files
    filename = f'Data/random_atsp_instance{i}.atsp'
    distances = read_atsp_data(filename)
    num_colonies = max(max(i, j) for i, j in distances) + 1

    for model in ["DFJ", "MTZ", "GG"]:
        results = solve_atsp_model(model, distances, num_colonies)
        results_data.append(results)

# Write results to a CSV file
with open(output_csv, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["File", "Model", "Status", "Total Distance", "Computation Time"])

    for result in results_data:
        writer.writerow([result["File"], result["Model"], result["Status"], result["Total Distance"], result["Computation Time"]])