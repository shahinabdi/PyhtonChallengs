### 26 — itertools Fluency
```python
from itertools import *

def chunked(iterable, size):      # [1,2,3,4,5], 2 -> [1,2],[3,4],[5]
    ...
def pairwise_deltas(nums):        # [3,7,4] -> [4,-3]
    ...
def run_lengths(s):               # "aaabbc" -> [("a",3),("b",2),("c",1)]
    ...
def round_robin(*iters):          # "AB","12","xyz" -> A1xB2yz... (order: A,1,x,B,2,y,z)
    ...
```
**Complete:** Implement each using itertools primitives (`islice`, `pairwise`, `groupby`, `cycle`, `chain`, ...) — no manual index bookkeeping, all lazy.
