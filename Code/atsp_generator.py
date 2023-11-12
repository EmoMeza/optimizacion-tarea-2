import random

def generate_atsp_file(file_name, num_nodes, max_distance=100):
    """
    Generates an ATSP file with random distances between nodes.
    
    :param file_name: Name of the file to be generated.
    :param num_nodes: Number of nodes (cities or colonies) in the ATSP problem.
    :param max_distance: Maximum possible distance between any two nodes.
    """
    with open(file_name, 'w') as file:
        file.write("NAME: Random ATSP Instance\n")
        file.write("TYPE: ATSP\n")
        file.write(f"DIMENSION: {num_nodes}\n")
        file.write("EDGE_WEIGHT_TYPE: EXPLICIT\n")
        file.write("EDGE_WEIGHT_FORMAT: FULL_MATRIX\n")
        file.write("EDGE_WEIGHT_SECTION\n")

        for i in range(num_nodes):
            distances = [random.randint(1, max_distance) if i != j else 9999 for j in range(num_nodes)]
            distance_line = ' '.join(map(str, distances)) + '\n'
            file.write(distance_line)

        file.write("EOF\n")

# Example usage
generate_atsp_file('./Data/random_atsp_instance2.atsp', num_nodes=12, max_distance=20)
