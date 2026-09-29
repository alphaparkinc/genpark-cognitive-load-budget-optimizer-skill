"""Client module for CognitiveLoadBudgetOptimizer (100% Python Standard Library)."""
import json
import time
import re
from typing import Dict, Any, List, Optional

class CognitiveLoadBudgetOptimizer:
    """Manages token budgets, latency SLAs, reasoning trace pruning,
    and adaptive cost-effective model routing."""
    
    MODEL_TIERS = {
        "fast_lite": {"name": "Flash-Lite / Haiku", "input_cost_per_m": 0.15, "output_cost_per_m": 0.60, "max_context": 128000},
        "standard": {"name": "Flash / Sonnet", "input_cost_per_m": 3.00, "output_cost_per_m": 15.00, "max_context": 200000},
        "deep_reasoning": {"name": "Pro / Opus / Reasoning", "input_cost_per_m": 15.00, "output_cost_per_m": 75.00, "max_context": 200000}
    }

    def __init__(self, max_token_budget: int = 120000, max_cost_budget_usd: float = 2.00):
        self.max_token_budget = max_token_budget
        self.max_cost_budget_usd = max_cost_budget_usd
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost_usd = 0.0
        self.interaction_turns = 0

    def track_usage(self, prompt_tokens: int, completion_tokens: int, model_tier: str = "standard") -> Dict[str, Any]:
        """Logs tokens consumed in an agent step and calculates accurate cost."""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.interaction_turns += 1
        
        tier = self.MODEL_TIERS.get(model_tier, self.MODEL_TIERS["standard"])
        step_cost = (prompt_tokens / 1_000_000.0 * tier["input_cost_per_m"]) + (completion_tokens / 1_000_000.0 * tier["output_cost_per_m"])
        self.total_cost_usd += step_cost
        
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        token_pct = (total_tokens / self.max_token_budget) * 100.0
        cost_pct = (self.total_cost_usd / self.max_cost_budget_usd) * 100.0
        
        warning = None
        if token_pct >= 85.0 or cost_pct >= 85.0:
            warning = "CRITICAL_HEADROOM_EXHAUSTION: Immediate context pruning and compression required."
        elif token_pct >= 70.0 or cost_pct >= 70.0:
            warning = "APPROACHING_BUDGET_CEILING: Recommend routing sub-tasks to fast_lite tier."
            
        return {
            "status": "success",
            "turn": self.interaction_turns,
            "step_tokens": prompt_tokens + completion_tokens,
            "step_cost_usd": round(step_cost, 5),
            "cumulative_tokens": total_tokens,
            "token_budget_used_pct": round(token_pct, 1),
            "cumulative_cost_usd": round(self.total_cost_usd, 4),
            "cost_budget_used_pct": round(cost_pct, 1),
            "warning": warning
        }

    def compress_trace(self, reasoning_trace: str, target_ratio: float = 0.35) -> Dict[str, Any]:
        """Prunes repetitive thoughts, verbose inner monologues, and retains key decision milestones."""
        original_len = len(reasoning_trace)
        lines = [line.strip() for line in reasoning_trace.split("\n") if line.strip()]
        
        # Keep lines containing key action words or conclusions
        milestone_keywords = ["decided", "concluded", "action:", "tool:", "error:", "result:", "plan:", "success", "verified"]
        retained = []
        for line in lines:
            line_lower = line.lower()
            if any(k in line_lower for k in milestone_keywords) or line.startswith(("-", "*", "1.", "2.", "3.")):
                retained.append(line)
                
        # If still too long, sample evenly
        max_lines = max(5, int(len(lines) * target_ratio))
        if len(retained) > max_lines:
            step = len(retained) / max_lines
            retained = [retained[int(i * step)] for i in range(max_lines)]
            
        compressed = "\n".join(retained)
        compressed_len = len(compressed)
        ratio = (compressed_len / max(1, original_len)) * 100.0
        
        return {
            "status": "success",
            "original_chars": original_len,
            "compressed_chars": compressed_len,
            "compression_ratio_pct": round(ratio, 1),
            "tokens_saved_estimate": max(0, int((original_len - compressed_len) / 4)),
            "compressed_trace": compressed
        }

    def route_model(self, task_complexity: str = "moderate") -> Dict[str, Any]:
        """Recommends model tier based on task complexity and remaining budget runway."""
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        token_pct = (total_tokens / self.max_token_budget) * 100.0
        
        if token_pct > 80.0:
            recommended_tier = "fast_lite"
            rationale = "Budget ceiling near limit (>80% used). Downgrading to lightweight model."
        elif task_complexity == "critical_reasoning":
            recommended_tier = "deep_reasoning"
            rationale = "Task requires deep logical deduction and multi-step backtracking."
        elif task_complexity == "simple":
            recommended_tier = "fast_lite"
            rationale = "Lookup or straightforward formatting task suited for fast tier."
        else:
            recommended_tier = "standard"
            rationale = "Balanced general purpose task execution."
            
        return {
            "status": "success",
            "task_complexity": task_complexity,
            "recommended_tier": recommended_tier,
            "model_info": self.MODEL_TIERS[recommended_tier],
            "rationale": rationale
        }

    def get_budget_status(self) -> Dict[str, Any]:
        """Returns full overview of current consumption and headroom."""
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        return {
            "status": "success",
            "turns_recorded": self.interaction_turns,
            "tokens_consumed": total_tokens,
            "token_budget_max": self.max_token_budget,
            "token_budget_remaining": max(0, self.max_token_budget - total_tokens),
            "token_used_pct": round((total_tokens / self.max_token_budget) * 100.0, 1),
            "cost_consumed_usd": round(self.total_cost_usd, 4),
            "cost_budget_max_usd": self.max_cost_budget_usd,
            "cost_budget_remaining_usd": round(max(0.0, self.max_cost_budget_usd - self.total_cost_usd), 4),
            "cost_used_pct": round((self.total_cost_usd / self.max_cost_budget_usd) * 100.0, 1)
        }
