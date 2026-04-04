import os
import asyncio
os.environ["FSO_ROLE"] = "EXECUTOR"
from fso_unified_kernel import run_unified_cycle
if __name__ == "__main__":
    asyncio.run(run_unified_cycle())
