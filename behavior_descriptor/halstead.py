import sys
import os
import inspect
from radon.metrics import h_visit

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

from utils.utils import get_heuristic_name
import gpt

#Detect which heuristic function is defined
possible_func_names = ["heuristics", "heuristics_v1", "heuristics_v2", "heuristics_v3"]
heuristic_name = get_heuristic_name(gpt, possible_func_names)
heuristic_func = getattr(gpt, heuristic_name)

#Get source of the function
source = inspect.getsource(heuristic_func)

#Analyze with radon.metrics.h_visit (Halstead)
metrics = h_visit(source)

total = metrics.total

print(f"{total.vocabulary}")

