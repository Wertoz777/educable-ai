class Metrics:
    def __init__(self):
        self.events = []  # ("type", payload)

    def log(self, k, v): self.events.append((k, v))

    def kpis(self):
        return {
            "harm_reduction": self._calc_harm_reduction(),
            "trust_score": self._trust_survey_mean(),   # 0..1
            "adaptation_time": self._avg_adaptation_time()
        }