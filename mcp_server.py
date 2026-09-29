"""MCP JSON-RPC stdio server for genpark-cognitive-load-budget-optimizer-skill."""
import sys
import json
from client import CognitiveLoadBudgetOptimizer

optimizer = CognitiveLoadBudgetOptimizer()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "optimize_cognitive_budget":
        return {"error": f"Unknown tool '{name}'"}
        
    action = args.get("action")
    if action == "track_usage":
        return optimizer.track_usage(
            prompt_tokens=args.get("prompt_tokens", 0),
            completion_tokens=args.get("completion_tokens", 0),
            model_tier=args.get("model_tier", "standard")
        )
    elif action == "compress_trace":
        return optimizer.compress_trace(
            reasoning_trace=args.get("reasoning_trace", "")
        )
    elif action == "route_model":
        return optimizer.route_model(
            task_complexity=args.get("task_complexity", "moderate")
        )
    elif action == "get_budget_status":
        return optimizer.get_budget_status()
    else:
        return {"error": f"Unknown action '{action}'"}

def main():
    if "--test" in sys.argv:
        print("[TEST] Running self-test for CognitiveLoadBudgetOptimizer...")
        t_res = optimizer.track_usage(2500, 450)
        assert t_res["status"] == "success"
        r_res = optimizer.route_model("critical_reasoning")
        assert r_res["recommended_tier"] == "deep_reasoning"
        sample_trace = "Thought 1: inspect page\nAction: fetch_url\nResult: 200 OK\nDecided to proceed with parse\nPlan: done"
        c_res = optimizer.compress_trace(sample_trace)
        assert c_res["compressed_chars"] > 0
        print(f"[TEST] Success! Tokens saved estimate: {c_res['tokens_saved_estimate']}")
        return

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "optimize_cognitive_budget",
                                "description": "Audit token & monetary budget, compress verbose reasoning traces, and recommend optimal model routing tier.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string", "enum": ["track_usage", "compress_trace", "route_model", "get_budget_status"]},
                                        "prompt_tokens": {"type": "integer"},
                                        "completion_tokens": {"type": "integer"},
                                        "cost_usd": {"type": "number"},
                                        "reasoning_trace": {"type": "string"},
                                        "task_complexity": {"type": "string", "enum": ["simple", "moderate", "complex", "critical_reasoning"]}
                                    },
                                    "required": ["action"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
