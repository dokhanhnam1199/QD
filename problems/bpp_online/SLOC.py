import sys
import os
import inspect
from radon.raw import analyze
sys.path.insert(0, "../../../")

from gpt import priority_v2 as priority

# Get the source code of the function
source = inspect.getsource(priority)

# Analyze SLOC with radon.raw.analyze
raw_metrics = analyze(source)

# Print metrics
print(f"{raw_metrics.sloc}")