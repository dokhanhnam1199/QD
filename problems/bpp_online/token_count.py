import sys
import os
import inspect
import tokenize
import io

sys.path.insert(0, "../../../")

from gpt import priority_v2 as priority

# Get the source code of the function
source = inspect.getsource(priority)

# Count number of tokens
tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
print(f"{len(tokens)}")
