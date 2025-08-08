import numpy as np
from typing import Optional, Union

def priority_v2(
    item: float,
    bins_remain_cap: np.ndarray,
    *,
    step: int = 0,
    epsilon0: float = 0.20,
    decay_rate: float = 0.01,
    alpha: float = 10.0,
    exact_bonus: float = 1e6,
    tolerance: float = 1e-12,
    random_state: Optional[Union[int, np.random.Generator]] = None,
) -> np.ndarray:
    """
    Compute priority scores for bins in an online Bin Packing Problem (BPP).

    The heuristic favours bins that become tightly packed after placing the
    item. It uses a logistic transform of the normalised slack, adaptive to the
    current set of feasible bins, a large bonus for exact fits, deterministic
    jitter for tie‑breaking, and an ε‑greedy exploration strategy with a decaying
    ε.

    Parameters
    ----------
    item : float
        Size of the incoming item.
    bins_remain_cap : np.ndarray
        1‑D array with the remaining capacity of each currently open bin.
    step : int, optional
        Number of items already processed; used to decay ε. Default is 0.
    epsilon0 : float, optional
        Initial exploration probability. Default is 0.20.
    decay_rate : float, optional
        Decay factor for ε (ε = ε₀ / (1 + decay_rate * step)). Default is 0.01.
    alpha : float, optional
        Steepness of the logistic curve. Larger values give a sharper transition.
        Default is 10.0.
    exact_bonus : float, optional
        Bonus added to exact‑fit bins to guarantee their selection.
        Default is 1e6.
    tolerance : float, optional
        Numerical tolerance for floating‑point comparisons.
        Default is 1e-12.
    random_state : int | np.random.Generator | None, optional
        Seed or generator for the random numbers used in ε‑greedy exploration.
        Default is None (uses NumPy's default RNG).

    Returns
    -------
    np.ndarray
        Priority scores for each bin; infeasible bins have ``-np.inf``.
    """
    # Convert to a float64 NumPy array
    caps = np.asarray(bins_remain_cap, dtype=np.float64)

    # Initialise priority vector with -inf for infeasible bins
    priority = np.full_like(caps, -np.inf, dtype=np.float64)

    # Feasibility mask: bin must have enough free space (allow tolerance)
    feasible = caps >= (item - tolerance)

    if not feasible.any():
        # No bin can accommodate the item
        return priority

    # Slack after placing the item (meaningful only for feasible bins)
    slack = caps - item

    # Exact‑fit detection (|slack| <= tolerance)
    exact_fit = np.abs(slack) <= tolerance
    priority[exact_fit] = exact_bonus

    # Non‑exact feasible bins
    non_exact = feasible & ~exact_fit

    if non_exact.any():
        # Representative capacity: largest remaining capacity among feasible bins
        capacity_est = caps[feasible].max()
        capacity_est = max(capacity_est, tolerance)  # avoid division by zero

        # Normalised slack ∈ [0, 1] (0 = perfect fit, 1 = empty bin)
        norm_slack = slack[non_exact] / capacity_est

        # Fit quality: larger when slack is smaller
        fit_quality = 1.0 - norm_slack  # 1 = perfect fit, 0 = empty bin

        # Adaptive midpoint: median fit quality of current feasible set
        median_fit = np.median(fit_quality)

        # Logistic transform: tighter fits get scores > 0.5
        logistic_arg = alpha * (fit_quality - median_fit)
        logistic_score = 1.0 / (1.0 + np.exp(-logistic_arg))

        # Deterministic jitter based on bin index to break ties
        idx = np.where(non_exact)[0]
        jitter = 1e-12 * (idx.astype(np.float64) / (len(caps) + 1.0))

        priority[non_exact] = logistic_score + jitter

    # ------------------------------------------------------------------
    # ε‑greedy exploration (decaying ε)
    # ------------------------------------------------------------------
    epsilon = epsilon0 / (1.0 + decay_rate * step)

    # Initialise RNG
    if isinstance(random_state, np.random.Generator):
        rng = random_state
    else:
        rng = np.random.default_rng(random_state)

    if rng.random() < epsilon:
        # Exploration: assign uniform random scores to feasible non‑exact bins
        rand_vals = rng.random(non_exact.sum())
        priority[non_exact] = rand_vals
        # Preserve exact‑fit bonus
        priority[exact_fit] = exact_bonus

    return priority
