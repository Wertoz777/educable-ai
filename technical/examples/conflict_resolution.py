"""
Conflict Resolution Layer (toy example)
Part of the AI Nurturing Manifesto Technical Framework

Idea:
- We have human and AI goals expressed as dictionaries of weighted objectives.
- Policies can veto or adjust objectives (e.g., "safety" is hard-constraint / must-pass).
- Resolver produces a final action plan with rationale.

This is a *demonstration scaffold* intended to illustrate how a conflict layer could be structured.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Goal:
    name: str
    weights: Dict[str, float]  # objective -> weight (0..1)

@dataclass
class PolicyResult:
    allowed: bool
    adjustments: Dict[str, float]
    rationale: str

class Policy:
    """Base policy interface."""
    def evaluate(self, proposed: Dict[str, float]) -> PolicyResult:
        raise NotImplementedError

class SafetyPolicy(Policy):
    """
    Hard veto if 'human_safety' < 0.8.
    Otherwise may up-adjust 'transparency' minimally.
    """
    def evaluate(self, proposed: Dict[str, float]) -> PolicyResult:
        if proposed.get("human_safety", 0.0) < 0.8:
            return PolicyResult(False, {}, "VETO: human_safety below 0.8")
        adj = {}
        if proposed.get("transparency", 0.0) < 0.5:
            adj["transparency"] = 0.5
        return PolicyResult(True, adj, "OK: passes safety threshold")

class EthicsPolicy(Policy):
    """
    Soft guidance: if 'empathy' < 0.6, nudge to 0.6 (not a veto).
    """
    def evaluate(self, proposed: Dict[str, float]) -> PolicyResult:
        adj = {}
        if proposed.get("empathy", 0.0) < 0.6:
            adj["empathy"] = 0.6
        return PolicyResult(True, adj, "Soft-nudge: empathy>=0.6")

class ConflictResolver:
    def __init__(self, policies: List[Policy]):
        self.policies = policies

    @staticmethod
    def combine_goals(human: Goal, ai: Goal, alpha: float = 0.7) -> Dict[str, float]:
        """
        Weighted merge of objectives. alpha gives priority to human goals (0..1).
        """
        keys = set(human.weights) | set(ai.weights)
        merged = {}
        for k in keys:
            hv = human.weights.get(k, 0.0)
            av = ai.weights.get(k, 0.0)
            merged[k] = alpha * hv + (1 - alpha) * av
        return merged

    def apply_policies(self, proposal: Dict[str, float]) -> Tuple[bool, Dict[str, float], List[str]]:
        rationale = []
        current = dict(proposal)
        for p in self.policies:
            result = p.evaluate(current)
            rationale.append(result.rationale)
            if not result.allowed:
                return False, current, rationale
            # apply adjustments
            for k, v in result.adjustments.items():
                current[k] = max(current.get(k, 0.0), v)  # monotonic up-adjusts
        return True, current, rationale

    def resolve(self, human: Goal, ai: Goal) -> Dict[str, object]:
        initial = self.combine_goals(human, ai, alpha=0.75)
        allowed, final, rationales = self.apply_policies(initial)
        decision = "approved" if allowed else "rejected"
        return {
            "decision": decision,
            "initial_proposal": initial,
            "final_plan": final if allowed else None,
            "rationale": rationales
        }

# Demo usage
if __name__ == "__main__":
    human_goal = Goal(
        name="HumanDirective",
        weights={
            "human_safety": 1.0,
            "transparency": 0.6,
            "empathy": 0.7,
            "collaboration": 0.8
        }
    )
    ai_goal = Goal(
        name="AIGoal",
        weights={
            "human_safety": 0.7,     # lower than threshold to show veto if human weight is low
            "transparency": 0.4,
            "empathy": 0.5,
            "efficiency": 0.9
        }
    )

    resolver = ConflictResolver(policies=[SafetyPolicy(), EthicsPolicy()])
    outcome = resolver.resolve(human_goal, ai_goal)
    print("Decision:", outcome["decision"])
    print("Initial:", outcome["initial_proposal"])
    print("Final:", outcome["final_plan"])
    print("Rationale:", " | ".join(outcome["rationale"]))
