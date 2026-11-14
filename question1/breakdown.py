import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from question1.agent import SupportCopilot

c = SupportCopilot()
for tid in ["T-1001", "T-1002", "T-1003", "T-1004"]:
    c.handle_ticket(tid)
for tid, call in zip(["T-1001", "T-1002", "T-1003", "T-1004"], c.session.calls):
    cached = min(call.cached_prefix_tokens, call.input_tokens)
    uncached = call.input_tokens - cached
    print(
        f"{tid}: uncached_in={uncached} cached_in={cached} "
        f"out={call.output_tokens} points={call.points()} "
        f"({uncached}*3 + {cached}*0.3 + {call.output_tokens}*15)"
    )
print("TOTAL", c.session.total_points())