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

    # 1. Feasibility: Huge priority boost for bins that can fit the item.
    can_fit = bins_remain_cap >= item
    if not np.any(can_fit):
        return priorities - 100  # Return negative priorities if no bin can fit

    priorities[can_fit] += 1000  # Significant base priority

    # 2. Wasted Space: Minimize wasted space within feasible bins.
    waste = bins_remain_cap[can_fit] - item
    # Using an inverse function to heavily reward minimal waste.  Small waste -> high value. Add a small constant to avoid division by zero.
    priorities[can_fit] += 500 / (waste + 0.001)

    # 3. Explicit Infeasibility Penalty: Negative priority for bins that can't fit.
    priorities[~can_fit] -= 100

    # 4. Fullness Reward: Prefer bins that are already somewhat full. Normalize for consistent scaling.
    total_capacity = np.sum(bins_remain_cap)
    if total_capacity > 0:
        priorities += 100 * (1 - bins_remain_cap / total_capacity)
    else:
        priorities += 1  #If all are zero capacity.

    # 5. Controlled Randomness:  Introduce a small amount of randomness to explore solutions.
    randomness_factor = 10
    priorities += np.random.rand(len(bins_remain_cap)) * randomness_factor

    return priorities
