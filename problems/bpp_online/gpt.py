import numpy as np
import random
import math
import scipy
import torch
def priority_v2(item: float, bins_remain_cap: np.ndarray, not_enough_space_priority: float = -1656.2260420197204, avoid_division_by_zero_constant: float = 0.046569358506945074, space_priority_scaler: float = 0.5627930301739644) -> np.ndarray:
    """Returns priority with which we want to add item to each bin.
    This version prioritizes bins that have enough space and minimizes wasted space.
    If a bin doesn't have enough space, it gets a very low priority.
    Otherwise, the priority is higher if the remaining space after packing the item is smaller.

    Args:
        item: Size of item to be added to the bin.
        bins_remain_cap: Array of capacities for each bin.
        not_enough_space_priority: Priority assigned to bins that can't fit the item.
        avoid_division_by_zero_constant: Small constant added to avoid division by zero.
        space_priority_scaler: Scales the inverse of the remaining space.

    Return:
        Array of same size as bins_remain_cap with priority score of each bin.
    """
    priorities = np.zeros_like(bins_remain_cap, dtype=float)
    for i, capacity in enumerate(bins_remain_cap):
        if capacity >= item:
            remaining_space = capacity - item
            # Give higher priority to bins with less remaining space
            priorities[i] = space_priority_scaler / (remaining_space + avoid_division_by_zero_constant)  # Add a small constant to avoid division by zero
        else:
            # Assign a very low priority to bins that can't fit the item
            priorities[i] = not_enough_space_priority  # Or some other very negative value
    return priorities
