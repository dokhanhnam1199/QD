import numpy as np

def priority_v2(item: float, bins_remain_cap: np.ndarray) -> np.ndarray:
    """Returns priority with which we want to add item to each bin using Softmax-Based Fit.

    This function implements a "Softmax-Based Fit" strategy for online bin packing.
    The core idea is to assign a 'raw fit score' to each bin based on how well it
    accommodates the current item. Bins that result in a smaller remaining capacity
    (a "tighter" fit) receive higher raw scores. These raw scores are then
    transformed using the softmax function to produce normalized priority scores.

    A bin that cannot fit the item is assigned a very low raw score, ensuring its
    priority after softmax is effectively zero.

    Args:
        item: Size of item to be added to the bin.
        bins_remain_cap: A NumPy array containing the remaining capacities of each bin.

    Returns:
        A NumPy array of the same size as bins_remain_cap, where each element
        represents the priority score for the corresponding bin. These scores
        will sum to 1.0 if at least one bin can accommodate the item. If no bin
        can accommodate the item, all priorities will be 0.
    """
    # Initialize raw scores for all bins to a very low value.
    # This ensures that bins which cannot fit the item will have their
    # exponential term become effectively zero, resulting in zero priority.
    raw_fit_scores = np.full_like(bins_remain_cap, -np.inf, dtype=float)

    # Create a boolean mask for bins that can accommodate the current item.
    can_fit_mask = bins_remain_cap >= item

    # For bins that can fit, calculate their raw fit score.
    # The score is calculated as (item - remaining_capacity).
    # A perfect fit (remaining_capacity == item) yields a score of 0, which is the
    # highest possible score in this formulation (indicating the tightest fit).
    # Looser fits (larger remaining_capacity) yield more negative scores.
    # Example: item=0.5
    #   - Bin with capacity 0.5: score = 0.5 - 0.5 = 0.0 (perfect fit, highest score)
    #   - Bin with capacity 0.7: score = 0.5 - 0.7 = -0.2 (tighter fit than 1.0)
    #   - Bin with capacity 1.0: score = 0.5 - 1.0 = -0.5 (looser fit, lower score)
    raw_fit_scores[can_fit_mask] = item - bins_remain_cap[can_fit_mask]

    # Apply the exponential function to the raw scores.
    # np.exp(-np.inf) correctly evaluates to 0.0, handling non-fitting bins.
    exp_scores = np.exp(raw_fit_scores)

    # Calculate the sum of the exponential scores. This will be used for normalization.
    sum_exp_scores = np.sum(exp_scores)

    # Compute the final priorities using softmax normalization.
    if sum_exp_scores == 0:
        # If sum_exp_scores is 0, it means no bin could fit the item (all raw_fit_scores were -np.inf).
        # In this case, all priorities are 0, indicating no suitable bin was found.
        priorities = np.zeros_like(bins_remain_cap, dtype=float)
    else:
        # Normalize the exponential scores to obtain probabilities/priorities that sum to 1.
        priorities = exp_scores / sum_exp_scores

    return priorities
