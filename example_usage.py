"""Example usage for CognitiveLoadBudgetOptimizer."""
import json
from client import CognitiveLoadBudgetOptimizer

def main():
    print("=== Cognitive Load Budget Optimizer Demo ===")
    opt = CognitiveLoadBudgetOptimizer(max_token_budget=50000, max_cost_budget_usd=1.00)
    
    # 1. Track step usage
    res = opt.track_usage(prompt_tokens=4500, completion_tokens=850, model_tier="standard")
    print("Usage Step 1:", json.dumps(res, indent=2))
    
    # 2. Compress verbose thinking trace
    trace = """
    Step 1: Reading user query.
    Thinking: The user wants to know if AAPL stock is up.
    I should check external tool.
    Tool: finance_api.query(symbol='AAPL')
    Result: AAPL is 224.5 (+1.2%)
    Decided to draft concise response.
    Conclusion: Report AAPL gain.
    """
    comp = opt.compress_trace(trace)
    print("Compressed Trace Result:", json.dumps(comp, indent=2))
    
    # 3. Model routing recommendation
    route = opt.route_model("critical_reasoning")
    print("Routing Recommendation:", json.dumps(route, indent=2))
    
    # 4. Budget status
    status = opt.get_budget_status()
    print("Overall Budget Status:", json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
