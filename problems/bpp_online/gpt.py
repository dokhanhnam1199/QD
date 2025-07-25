import numpy as np

def priority_v2(item: float, bins_remain_cap: np.ndarray) -> np.ndarray:
    """
    Returns priority with which we want to add item to each bin.

    This priority function prioritizes exact fits, optimizes remaining capacity, and penalizes overfills.
    If a bin has a remaining capacity that exactly matches the item size, it gets the highest priority.
    Otherwise, bins with lower remaining capacities are prioritized over those with higher remaining capacities,
    to ensure that bins are fully utilized.

    Args:
        item: Size of item to be added to the bin.
        bins_remain_cap: Array of capacities for each bin.

    Return:
        Array of same size as bins_remain_cap with priority score of each bin.
    """
    valid_bins = bins_remain_cap >= item
    exact_fits = bins_remain_cap == item
    priority_scores = np.where(exact_fits, 2, 0) + np.where(valid_bins, 1 - (bins_remain_cap / (bins_remain_cap + item)), 0)
    return priority_scores
