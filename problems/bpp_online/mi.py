import sys
import os
import inspect
from radon.metrics import mi_visit
sys.path.insert(0, "../../../")

from gpt import priority_v2 as priority

# Get the source code of the function
source = inspect.getsource(priority)

# Analyze Maintainability Index
mi_score = mi_visit(source, True)  # Set True to get an average for the module
print(f"{mi_score}")
