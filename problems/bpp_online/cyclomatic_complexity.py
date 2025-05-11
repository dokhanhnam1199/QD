import sys
import os
import inspect
from radon.complexity import cc_visit
sys.path.insert(0, "../../../")

from gpt import priority_v2 as priority

# Get the source code of the function
source = inspect.getsource(priority)

# Analyze Cyclomatic Complexity
complexities = cc_visit(source)
obj = complexities[0]
print(f"{obj.complexity}")