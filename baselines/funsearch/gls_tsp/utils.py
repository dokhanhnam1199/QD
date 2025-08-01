specification = r'''
import numpy as np


@funsearch.run
def evaluate():
    """Empty function. Use eval_helper.
    """
    raise Exception('Do not invoke @funsearch.run() in Sandbox.')


@funsearch.evolve
def update_edge_distance(edge_distance: np.ndarray, local_opt_tour: np.ndarray, edge_n_used: np.ndarray) -> np.ndarray:
    """
    Args:
        edge_distance (np.ndarray): Original edge distance matrix.
        local_opt_tour (np.ndarray): Local optimal solution path.
        edge_n_used (np.ndarray): Matrix representing the number of times each edge is used.
    Return:
        updated_edge_distance: updated score of each edge distance matrix.
    """ 
    # Assuming edge_distance, local_opt_tour, and edge_n_used have compatible shapes
    num_nodes = edge_distance.shape[0]

    # Initialize an array to store the updated edge distances
    updated_edge_distance = np.copy(edge_distance)

    # Iterate over the edges in the local optimal tour
    for i in range(num_nodes - 1):
        current_node = local_opt_tour[i]
        next_node = local_opt_tour[i + 1]

        # Update the edge distance based on the number of times it has been used
        updated_edge_distance[current_node, next_node] *= (1 + edge_n_used[current_node, next_node])

    # Update the last edge in the tour
    updated_edge_distance[local_opt_tour[-1], local_opt_tour[0]] *= (1 + edge_n_used[local_opt_tour[-1], local_opt_tour[0]])

    return updated_edge_distance
'''



