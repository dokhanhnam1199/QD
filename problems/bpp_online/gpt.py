def priority_v2(item, bins_remain_cap):
    """{Assigns a priority score to each bin based on the remaining capacity and item size, favoring bins with capacity closest to the item size and penalizing bins that are too full or too empty.}"""
    priority = []
    for cap in bins_remain_cap:
        if cap >= item:
            priority.append(1 / (abs(cap - item) + 0.0001) - (cap / sum(bins_remain_cap)))
        else:
            priority.append(-1000)  # Penalize bins that are too small
    return priority
