class ArbitrationLayer:
    def __init__(self, voters): self.voters = voters
    def consensus(self, proposal):
        ballots = [v.cast_vote(proposal) for v in self.voters]
        score = sum(b["weight"]*(1 if b["approve"] else -1) for b in ballots)
        return {"approved": score > 0, "score": score, "ballots": ballots}