import numpy as np

def heuristics_v2(distance_matrix):
    """{This algorithm uses a nearest neighbor approach to generate initial tours, improves them with 2-opt, and aggregates edge frequencies weighted by an exponential function of tour rank based on their lengths.}"""
    n = distance_matrix.shape[0]
    num_tours = 50
    edge_counts = np.zeros_like(distance_matrix)

    tours = []
    tour_lengths = []

    for _ in range(num_tours):
        # Generate initial tour using nearest neighbor
        start_node = np.random.randint(n)
        tour = [start_node]
        unvisited = set(range(n))
        unvisited.remove(start_node)

        while unvisited:
            last_node = tour[-1]
            nearest_node = min(unvisited, key=lambda x: distance_matrix[last_node, x])
            tour.append(nearest_node)
            unvisited.remove(nearest_node)
        tour.append(tour[0])

        # 2-opt local search
        improved = True
        while improved:
            improved = False
            for i in range(1, n - 1):
                for k in range(i + 1, n):
                    current_cost = distance_matrix[tour[i-1], tour[i]] + distance_matrix[tour[k], tour[k+1]]
                    new_cost = distance_matrix[tour[i-1], tour[k]] + distance_matrix[tour[i], tour[k+1]]

                    if new_cost < current_cost:
                        tour[i:k+1] = tour[i:k+1][::-1]
                        improved = True

        tour_length = sum(distance_matrix[tour[i], tour[i+1]] for i in range(n))
        tours.append(tour)
        tour_lengths.append(tour_length)

    # Rank tours based on length
    ranked_indices = np.argsort(tour_lengths)

    for rank, index in enumerate(ranked_indices):
        tour = tours[index]
        # Weight edge counts by exponential function of rank
        weight = np.exp(-rank / 10.0)  # Exponential weighting

        for i in range(n):
            node1 = tour[i]
            node2 = tour[i+1]
            edge_counts[node1, node2] += weight
            edge_counts[node2, node1] += weight

    heuristics_matrix = np.zeros_like(distance_matrix, dtype=float)
    for i in range(n):
        for j in range(n):
            if distance_matrix[i, j] > 0:
                heuristics_matrix[i, j] = edge_counts[i, j] / distance_matrix[i, j]
            else:
                heuristics_matrix[i, j] = 0

    return heuristics_matrix
