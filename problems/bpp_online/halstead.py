import sys
import os
import inspect
from radon.metrics import h_visit
sys.path.insert(0, "../../../")

from gpt import priority_v2 as priority

# Get source of the function
source = inspect.getsource(priority)

# Analyze with radon.metrics.h_visit (Halstead)
metrics = h_visit(source)
total = metrics.total
print(f"{total.volume}")

