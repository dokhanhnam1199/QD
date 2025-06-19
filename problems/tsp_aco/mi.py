import sys
import os
import inspect
from radon.metrics import mi_visit
sys.path.insert(0, "../../../")

# Import target module and helper
import gpt
from utils.utils import get_heuristic_name

# Possible heuristic function names
possible_func_names = ["heuristics", "heuristics_v1", "heuristics_v2", "heuristics_v3"]

# Resolve the actual function
heuristic_name = get_heuristic_name(gpt, possible_func_names)
heuristic_func = getattr(gpt, heuristic_name)

# Get source code of the function
source = inspect.getsource(heuristic_func)

# Analyze Maintainability Index (returns a float if second arg is True)
mi_score = mi_visit(source, True)

print(f"{mi_score}")
