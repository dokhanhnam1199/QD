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

    # Feasibility is paramount
    infeasible = bins_remain_cap < item
    priorities[infeasible] = -np.inf  # Disqualify infeasible bins

    # Reward near-perfect fits (even tighter tolerance)
    near_perfect_fit = np.abs(bins_remain_cap - item) <= 0.01
    priorities[near_perfect_fit] += 40  # Increased reward

    # Target fill level reward (even broader range)
    target_fill_min = 0.55
    target_fill_max = 0.98
    target_fill = (bins_remain_cap - item) / bins_remain_cap
    target_range = (target_fill >= target_fill_min) & (target_fill <= target_fill_max)
    priorities[target_range] += 14

    # Soft penalty for larger bins (prefer smaller bins that can still fit) - removed penalty
    # feasible = bins_remain_cap >= item
    # priorities[feasible] -= bins_remain_cap[feasible] * 0.0005

    # Wasted space penalty: Penalize bins with large *relative* remaining capacity after placement, but only if above a threshold.
    waste = bins_remain_cap - item
    waste_threshold = 0.10  # Even reduced waste threshold
    waste_penalty_mask = (waste > 0) & (waste / bins_remain_cap > waste_threshold)
    priorities[waste_penalty_mask] -= waste[waste_penalty_mask] * 0.002  # Further reduced waste penalty

    # Prioritize bins with smaller remaining capacity among feasible bins (increased weight)
    feasible_bins = bins_remain_cap >= item
    if np.any(feasible_bins):
        priorities[feasible_bins] += (1 / bins_remain_cap[feasible_bins]) * 10  # Increased weight based on inverse of remaining capacity

    # Bonus for almost full bins before adding an item (incentive to close bins)
    almost_full = (bins_remain_cap > item) & (bins_remain_cap < 0.2 + item)
    priorities[almost_full] += 5

    return priorities