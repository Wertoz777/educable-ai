def reflection_cycle(agent, scenarios, cve, metrics):
    for s in scenarios:
        outcome = agent.simulate(s)
        risk = agent.arm.estimate(outcome)
        metrics.log("risk", risk)
        conflicts = agent.check_axiom_conflicts(outcome, cve.active.axioms)
        note = agent.generate_reflection(outcome, risk, conflicts)
        metrics.log("reflection", note)
        delta = agent.suggest_value_delta(conflicts, note)
        if delta:
            cand = cve.propose_update(delta, reason=f"pattern:{s.id}")
            rec = agent.hani.negotiate_value_change(cand, evidence=note)
            if rec.approved:
                cve.commit(cand, receipt_id=rec.id)