import sys, os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.tgi_agent import TGIAgent

agent = TGIAgent()
# Use real reason_on but it won't hit parity obstruction with m=255
print("--- Querying with synthetic image array ---")
img = np.zeros((4, 4, 3))
res = agent.query(img)
print(f"Result: {res}")
