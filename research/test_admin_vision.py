import sys, os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from research.tgi_agent import TGIAgent

agent = TGIAgent()
print("--- Querying with Admin Vision mode ---")
img = np.zeros((16, 16, 3))
img[4:12, 4:12] = [1, 0, 0]
res = agent.query(img, admin_vision=True)
print(res)
