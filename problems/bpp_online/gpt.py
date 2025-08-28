import numpy as np

def priority_v2(item: float, bins_remain_cap: np.ndarray) -> np.ndarray:
    """Returns priority with which we want to add item to each bin.

    Args:
        item: Size of item to be added to the bin.
        bins_remain_cap: Array of capacities for each bin.

    Returns:
        Array of same size as bins_remain_cap with priority score of each bin.
    """
    priorities = np.zeros_like(bins_remain_cap)
    # Calculate the ratio of item size to bin remaining capacity.
    # A smaller ratio means a better fit.  Avoid division by zero.
    ratios = np.where(bins_remain_cap > 0, item / bins_remain_cap, np.inf)
    # Prioritize bins with smaller ratios (better fit).  Use the inverse ratio.
    priorities = 1.0 / ratios
    # Penalize bins that are almost full (to encourage spreading items).
    priorities = priorities * (1.0 - (bins_remain_cap / 1.0))  # Assuming bin capacity is 1.0
    return priorities
