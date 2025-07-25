import numpy as np

def heuristics_v2(distance_matrix: np.ndarray, coordinates: np.ndarray, demands: np.ndarray, capacity: int) -> np.ndarray:
    """
    A heuristic function for the Capacitated Vehicle Routing Problem (CVRP).

    This version combines distance, demand, and a "savings" approach to
    prioritize edges.  It biases towards connecting nodes with smaller
    demands and shorter distances, and encourages connections that result in
    large savings (reduction in total travel distance) by connecting them.

    Args:
        distance_matrix (np.ndarray): A distance matrix of shape (n, n) where
                                      n is the number of nodes.
        coordinates (np.ndarray): Coordinates of the nodes (shape: n x 2).
        demands (np.ndarray): A vector of customer demands (shape: n).
        capacity (int): The capacity of the vehicles.

    Returns:
        np.ndarray: A matrix of the same shape as the distance_matrix,
                    representing the desirability of including each edge
                    in a solution. Higher values indicate more desirable edges.
    """

    n = distance_matrix.shape[0]
    heuristic_matrix = np.zeros((n, n))

    # Inverse distance, with a small constant to avoid division by zero
    inverse_distance = 1 / (distance_matrix + 1e-6)

    # Demand-based factor: penalize edges connecting high-demand nodes
    demand_factor = np.outer(demands, demands)
    demand_factor = 1 / (demand_factor + 1e-6) # Inverted to favor small demand


    # "Savings" calculation:  How much distance is saved by connecting i and j
    # instead of going i -> depot -> j
    savings = np.zeros((n, n))
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                savings[i, j] = distance_matrix[i, 0] + distance_matrix[0, j] - distance_matrix[i, j]


    # Combine factors
    heuristic_matrix = inverse_distance * demand_factor * (savings + 1) #Savings added, and offset by 1

    #Zero out depot-depot connections and self-connections
    for i in range(n):
        heuristic_matrix[i, i] = 0
    heuristic_matrix[0,0] = 0

    return heuristic_matrix
