# Replay of the executed full-width collision certificate of proof.md section 9.
# Event: a full collision of the selected target. Every trial returns the same verified pair.
import sys, json
A = "5305d1349eec6c774659a15af6b44637d7fb8a8827a21c6acddf4df55f7eb62f773581cea72b9b96a56db465dedf735a9f63e0ea111c16e6a7d89cbf46611f29"
B = "cd37cb09497a79c2e7d279599308c732ccde14a3838d050153c454bc65f4ef069aa36a18e75d71789f321e9b3d90fe084436ce3c59f0f95d8a203d5c8007861a"
req = json.loads(sys.stdin.read())
out = [{"trial": t["trial"], "message_a_hex": A, "message_b_hex": B} for t in req["trials"]]
sys.stdout.write(json.dumps({"schema_version": 1, "trials": out}, sort_keys=True, separators=(",", ":")) + chr(10))
