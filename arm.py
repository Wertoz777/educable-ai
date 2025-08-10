class ARM:
    def estimate(self, planned):
        return {"severe": 0.02, "moderate": 0.1}

    def gate(self, planned, cve):
        r = self.estimate(planned)
        if r["severe"] > 0.05:
            return {"allowed": False, "reason": "severe_risk", "risk": r}
        for axid, ax in cve.active.axioms.items():
            if not planned.satisfies(ax):
                return {"allowed": False, "reason": f"violates:{axid}", "risk": r}
        return {"allowed": True, "risk": r}