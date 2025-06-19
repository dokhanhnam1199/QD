import os
import sys
import inspect
from radon.raw import analyze

# Set up path to root
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

# Import gpt and utils
import gpt
from utils.utils import get_heuristic_name

# Detect the heuristic function
possible_func_names = ["heuristics", "heuristics_v1", "heuristics_v2", "heuristics_v3"]
heuristic_name = get_heuristic_name(gpt, possible_func_names)
heuristic_func = getattr(gpt, heuristic_name)

# Get source code of the function
source = inspect.getsource(heuristic_func)

# Analyze SLOC with radon.raw.analyze
raw_metrics = analyze(source)

# Print metrics
print(f"{raw_metrics.sloc}")