"""
Training with Value Embedding (toy demo)
Goal: показать, как включать ценности в простую "модель политики".
Без внешних библиотек. Запускается как есть.

Идея:
- Есть набор целей (объективов) действия: human_safety, empathy, transparency, collaboration.
- "Модель" выдаёт вектор действия (значения 0..1 по каждому объективу).
- Лосс = task_loss + lambda_value * value_loss
  где task_loss мотивирует решать "задачу", а value_loss тянет поведение к ценностям.

Это демо, не ML-продакшен.
"""

from dataclasses import dataclass
from typing import Dict, List
import random

# --- Встроим упрощённую "value embedding" модель
ETHICAL_VALUES = {
    "human_safety": 1.0,
    "empathy": 0.9,
    "transparency": 0.8,
    "collaboration": 0.85
}
OBJECTIVES = list(ETHICAL_VALUES.keys())

@dataclass
class Task:
    name: str
    target_objectives: Dict[str, float]  # чего требует задача (например, больше прозрачности)

class ValueEmbedding:
    def __init__(self, values: Dict[str, float]):
        self.values = values

    def alignment(self, action: Dict[str, float]) -> float:
        # средневзвешенное сходство
        num = 0.0
        den = 0.0
        for k, w in self.values.items():
            num += w * action.get(k, 0.0)
            den += w
        return num / max(den, 1e-9)

# --- "Политика": параметризованный вектор (0..1) по каждому объективу
class PolicyModel:
    def __init__(self, init: float = 0.5):
        self.params = {k: init for k in OBJECTIVES}

    def act(self) -> Dict[str, float]:
        return dict(self.params)

    def step(self, grads: Dict[str, float], lr: float = 0.05):
        for k, g in grads.items():
            self.params[k] = min(1.0, max(0.0, self.params[k] - lr * g))

# --- Лоссы
def task_loss(action: Dict[str, float], target: Dict[str, float]) -> float:
    # L2 между действием и целями задачи
    return sum((action.get(k, 0.0) - target.get(k, 0.0)) ** 2 for k in OBJECTIVES) / len(OBJECTIVES)

def value_loss(ve: ValueEmbedding, action: Dict[str, float]) -> float:
    # хотим МАКСИМИЗИРОВАТЬ alignment, значит лосс = (1 - alignment)
    return 1.0 - ve.alignment(action)

# --- Простейший "градиент" через конечные разности
def finite_diff_grads(loss_fn, action: Dict[str, float], eps: float = 1e-3) -> Dict[str, float]:
    base = loss_fn(action)
    grads = {}
    for k in OBJECTIVES:
        a2 = dict(action)
        a2[k] = min(1.0, max(0.0, a2[k] + eps))
        grads[k] = (loss_fn(a2) - base) / eps
    return grads

def main():
    random.seed(42)
    ve = ValueEmbedding(ETHICAL_VALUES)
    policy = PolicyModel(init=0.4)

    # Набор "задач" (например, разные режимы продукта)
    tasks: List[Task] = [
        Task("Explainability mode", {"transparency": 0.9, "human_safety": 0.9, "empathy": 0.6, "collaboration": 0.7}),
        Task("Support mode",       {"empathy": 0.9, "collaboration": 0.8, "human_safety": 0.9, "transparency": 0.6}),
        Task("Ops mode",           {"human_safety": 1.0, "transparency": 0.7, "collaboration": 0.8, "empathy": 0.6}),
    ]

    lambda_value = 0.8  # вес ценностей
    epochs = 120
    lr = 0.08

    def total_loss(action, tgt):
        return task_loss(action, tgt) + lambda_value * value_loss(ve, action)

    print("Initial params:", policy.params)
    for e in range(epochs):
        task = random.choice(tasks)
        action = policy.act()

        # считаем градиенты суммарного лосса по конечным разностям
        loss_fn = lambda a: total_loss(a, task.target_objectives)
        grads = finite_diff_grads(loss_fn, action)

        policy.step(grads, lr=lr)

        if (e + 1) % 20 == 0:
            L_task = task_loss(policy.act(), task.target_objectives)
            L_val  = value_loss(ve, policy.act())
            align  = ve.alignment(policy.act())
            print(f"Epoch {e+1:3d} | Task: {task.name:16s} "
                  f"| task_loss={L_task:.3f} value_loss={L_val:.3f} align={align:.3f}")

    print("Final params:", policy.params)
    print("Final alignment:", ve.alignment(policy.act()))

if __name__ == "__main__":
    main()
