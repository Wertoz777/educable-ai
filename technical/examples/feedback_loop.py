"""
Feedback Loop System Example
Part of the AI Nurturing Manifesto Technical Framework
"""

class FeedbackLoop:
    def __init__(self):
        self.rewards = []

    def give_feedback(self, ethical_score):
        if ethical_score >= 0.8:
            reward = "positive"
        elif ethical_score >= 0.5:
            reward = "neutral"
        else:
            reward = "negative"
        self.rewards.append((ethical_score, reward))
        return reward

# Example usage
if __name__ == "__main__":
    loop = FeedbackLoop()
    print(loop.give_feedback(0.9))  # Expected: positive
    print(loop.give_feedback(0.6))  # Expected: neutral
    print(loop.give_feedback(0.3))  # Expected: negative
