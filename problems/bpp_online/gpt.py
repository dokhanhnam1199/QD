def priority_v2(item, bins_remain_cap):
  """{This algorithm calculates a priority score for each bin based on a combination of remaining capacity and wasted space if the item is placed in the bin, favoring bins that can accommodate the item with minimal waste and penalizing those with insufficient capacity or large waste.}"""
  priority = []
  for cap in bins_remain_cap:
    if cap >= item:
      waste = cap - item
      priority.append(1 / (waste + 0.0001))  # Avoid division by zero
    else:
      priority.append(-1000)  # Large penalty for bins that can't fit the item
  return priority
