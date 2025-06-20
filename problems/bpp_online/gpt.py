def priority_v2(item, bins_remain_cap):
  """{Assigns a priority score to each bin based on its remaining capacity relative to the item size, favoring bins that are neither too full nor too empty after packing the item.}"""
  priority = []
  for cap in bins_remain_cap:
    if cap >= item:
      fill_ratio_after_packing = (item) / 100  # Assuming bin capacity is 100, prioritize based on fill ratio.
      priority.append(1 - abs(fill_ratio_after_packing - 0.5))  # Prefer bins that become half-full
    else:
      priority.append(-1)  # Invalid bin, assign lowest priority
  return priority
