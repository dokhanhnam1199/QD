import numpy as np

def priority_v2(item: float, bins_remain_cap: np.ndarray) -> np.ndarray:
    """Combines best-fit and inverse residual scoring with a large exact-fit bonus and tiny capacity tie‑breaker."""
    leftover = bins_remain_cap - item
    feasible = leftover >= 0
    priorities = np.full_like(bins_remain_cap, -np.inf, dtype=float)
    if np.any(feasible):
        priorities[feasible] = -leftover[feasible]
        priorities[feasible] += 1.0 / (1.0 + leftover[feasible])
        priorities[feasible & (leftover == 0)] += 1e6
        priorities[feasible] += 1e-6 * bins_remain_cap[feasible]
    return priorities