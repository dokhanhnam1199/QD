import inspect
import sys
import os
import tokenize
import io
sys.path.insert(0, "../../../")

# Import target module and helper
import gpt
from utils.utils import get_heuristic_name

possible_func_names = ["heuristics", "heuristics_v1", "heuristics_v2", "heuristics_v3"]
heuristic_name = get_heuristic_name(gpt, possible_func_names)
heuristic_func = getattr(gpt, heuristic_name)

# Get source code
source = inspect.getsource(heuristic_func)

# Count number of tokens
tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
token_count = len(tokens)

print(f"{token_count}")
