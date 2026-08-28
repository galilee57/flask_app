import random

class Game:

    GRID_W = 20
    GRID_H = 20

    def __init__(self):
        self.reset()

    # Modèle centralisé
    def to_dict(self):
        return {
            "grid": {
                "width": self.GRID_W,
                "height": self.GRID_H
            },
            "fruit": self.fruit,
            "snake": self.snake,
            "direction": self.direction,
            "score": self.score,
            "game_over": self.game_over,
            "steps_since_fruit": self.steps_since_fruit,
            "total_steps": self.total_steps,
            "message": self.message
        }

    def reset(self):
        self.snake = [
            {"x": 5, "y": 5},
            {"x": 4, "y": 5},
            {"x": 3, "y": 5}
        ]

        self.direction = "right"
        self.score = 0
        self.steps_since_fruit = 0
        self.total_steps = 0
        self.game_over = False
        self.message = ""
        self.fruit = self.generate_fruit()

    # Génération du fruit
    def generate_fruit(self):
        while True:
            fruit = {
                "x": random.randint(0, self.GRID_W - 1),
                "y": random.randint(0, self.GRID_H - 1)
            }

            # On empeche le fruit d'apparaitre sur le snake
            if fruit not in self.snake:
                return fruit