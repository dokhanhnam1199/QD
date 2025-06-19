import inspect
import sys
from radon.complexity import cc_visit

import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

from utils.utils import get_heuristic_name
# Load the gpt.py module
import gpt

# These are the possible heuristic function names
possible_func_names = ["heuristics", "heuristics_v1", "heuristics_v2", "heuristics_v3"]

# Get the correct heuristic function
heuristic_name = get_heuristic_name(gpt, possible_func_names)
heuristic_func = getattr(gpt, heuristic_name)

# Get the source code of the function
source = inspect.getsource(heuristic_func)

# Analyze Cyclomatic Complexity
complexities = cc_visit(source)
obj = complexities[0]
print(f"{obj.complexity}")