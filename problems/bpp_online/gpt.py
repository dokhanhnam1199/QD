import numpy as np

def priority_v2(item: float, bins_remain_cap: np.ndarray) -> np.ndarray:
    """Returns priority with which we want to add item to each bin using Softmax-Based Fit.

    The priority is calculated based on the remaining capacity of the bins.
    Bins with more remaining capacity are penalized (lower priority), encouraging
    the use of bins that are closer to being full. A small epsilon is added to
    avoid division by zero if a bin has zero remaining capacity.

    Args:
        item: Size of item to be added to the bin.
        bins_remain_cap: Array of remaining capacities for each bin.

    Return:
        Array of same size as bins_remain_cap with priority score of each bin.
    """
    epsilon = 1e-9  # Small value to prevent division by zero

    # Calculate the "fitness" for each bin: how well the item fits.
    # We want to prioritize bins where the item leaves less remaining space,
    # meaning the bin is more "full" after the item is added.
    # So, fitness is inversely related to the remaining capacity after adding the item.
    # We only consider bins where the item actually fits.
    fits = bins_remain_cap >= item
    fitness_scores = np.zeros_like(bins_remain_cap)
    fitness_scores[fits] = bins_remain_cap[fits] - item

    # Use softmax to convert fitness scores into probabilities (priorities).
    # We add epsilon to all fitness scores to ensure no non-positive values
    # are passed to exp, and to differentiate bins with zero remaining capacity
    # from bins where the item perfectly fits.
    # Higher fitness_scores (meaning less remaining capacity after packing)
    # will result in higher priority scores after softmax.
    adjusted_fitness_scores = fitness_scores + epsilon

    # Softmax formula: exp(x_i) / sum(exp(x_j))
    exp_scores = np.exp(adjusted_fitness_scores)
    sum_exp_scores = np.sum(exp_scores)

    # If all bins are full or the item doesn't fit anywhere, sum_exp_scores will be 0.
    # In such cases, return a uniform distribution or all zeros.
    if sum_exp_scores == 0:
        priorities = np.zeros_like(bins_remain_cap)
    else:
        priorities = exp_scores / sum_exp_scores

    return priorities
