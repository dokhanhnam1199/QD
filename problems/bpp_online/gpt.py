import numpy as np

def priority_v2(item: float, bins_remain_cap: np.ndarray) -> np.ndarray:
    """Returns priority with which we want to add item to each bin.
    Args:
        item: Size of item to be added to the bin.
        bins_remain_cap: Array of capacities for each bin.
    Returns:
        Array of same size as bins_remain_cap with priority score of each bin.
    """
    # Calculate the fit score for each bin
    fit_scores = item / bins_remain_cap

    # Exact fit gets a high boost
    exact_fit_mask = np.isclose(fit_scores, 1.0)
    fit_scores[exact_fit_mask] = 10.0

    # Reward good fits (between 0.5 and 1.0)
    good_fit_mask = (fit_scores > 0.5) & (fit_scores < 1.0)
    fit_scores[good_fit_mask] = fit_scores[good_fit_mask] * 5.0

    # Penalize nearly full bins
    fullness = 1 - (bins_remain_cap / np.max(bins_remain_cap))
    priorities = fit_scores * (1 - fullness * 0.7)

    # Reward bins with larger remaining capacities
    priorities = priorities + bins_remain_cap * 0.002

    # Ensure bins that are too small get a very low priority
    invalid_bins = bins_remain_cap < item
    priorities[invalid_bins] = 0.01

    # Add small random noise to encourage exploration
    priorities = priorities + np.random.rand(len(bins_remain_cap)) * 0.001

    return priorities
