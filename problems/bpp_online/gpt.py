import numpy as np

def priority_v2(item: float, bins_remain_cap: np.ndarray) -> np.ndarray:
    """Returns priority with which we want to add item to each bin.

    Args:
        item: Size of item to be added to the bin.
        bins_remain_cap: Array of capacities for each bin.

    Return:
        Array of same size as bins_remain_cap with priority score of each bin.
    """
    priorities = np.zeros_like(bins_remain_cap, dtype=float)

    # Feasibility: set priority to negative infinity for bins that can't fit the item
    infeasible_bins = bins_remain_cap < item
    priorities[infeasible_bins] = -np.inf

    # Reward tight fits: prioritize bins where the remaining space is small (but positive)
    remaining_space = bins_remain_cap - item
    feasible_bins = bins_remain_cap >= item

    # Avoid division by zero by adding a small epsilon
    epsilon = 1e-6
    max_cap = np.max(bins_remain_cap)

    priorities[feasible_bins] += 10.0 / (remaining_space[feasible_bins] + epsilon)  # Further increased tight fit priority

    # Fullness: boost priority for almost full bins (reduces fragmentation)
    almost_full_threshold = 0.1 * max_cap  # Further Adjusted threshold - more aggressive

    almost_full = feasible_bins & (remaining_space <= almost_full_threshold)
    # Scaling bonus based on proximity to being full, stronger scaling
    priorities[almost_full] += 30 * (1 - (remaining_space[almost_full] / almost_full_threshold))  # Substantially increased bonus

    # Penalize waste/overflow: give a penalty for bins with a lot of remaining space
    large_space_threshold = 0.4 * max_cap  # More aggressive threshold
    large_space = feasible_bins & (remaining_space > large_space_threshold)

    # Scale penalty based on the amount of waste, using a cubic penalty, much stronger.
    priorities[large_space] -= 10 * ((remaining_space[large_space] / max_cap)**3)  # Substantially increased penalty

    # Encourage Balanced bin usage, less aggressive than v1
    priorities[feasible_bins] += 0.005 * (bins_remain_cap[feasible_bins] / max_cap)

    # Discourage creating near-empty bins
    previously_almost_empty_threshold = 0.7 * max_cap  # adjusted threshold
    previously_almost_empty = (bins_remain_cap >= item) & (bins_remain_cap > previously_almost_empty_threshold) & (remaining_space > 0.5 * max_cap)  # adjusted Remaining space threshold for trigger
    priorities[previously_almost_empty] -= 10  # Significantly Increased penalty

    # Mildly penalize bins which are becoming half-full, to balance bin usage - stronger penalty
    half_full_threshold_high = 0.6 * max_cap
    half_full_threshold_low = 0.4 * max_cap
    becoming_half_full = feasible_bins & (bins_remain_cap > half_full_threshold_low) & (bins_remain_cap < half_full_threshold_high) & (remaining_space <= half_full_threshold_low)

    priorities[becoming_half_full] -= 4.0 # Increased penalty

    # Aggressively Penalize bins with remaining space > item * 2 - more aggressive
    double_item_space = feasible_bins & (remaining_space > item * 2)
    priorities[double_item_space] -= 8.0 * (remaining_space[double_item_space] / max_cap)  # increased effect

    # Penalize bins if item is very small compared to bin capacity, encourage using bins for items of appropriate size
    small_item_threshold = 0.1 * max_cap
    small_item_large_bin = feasible_bins & (item < small_item_threshold) & (bins_remain_cap > 0.6 * max_cap)
    priorities[small_item_large_bin] -= 3

    return priorities
