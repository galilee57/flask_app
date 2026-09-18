import random
from uuid import uuid4

class Game:

    GRID_W = 20
    GRID_H = 20

    def __init__(self, rng=None):
        self.rng = rng or random
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
            "message": self.message,
            "game_id": self.game_id,
            "mode": self.mode
        }

    def reset(self):
        self.game_id = uuid4().hex
        self.mode = None
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

    def next_head(self, direction):
        dx, dy = {"up": (0, -1), "right": (1, 0),
                  "down": (0, 1), "left": (-1, 0)}[direction]
        return {"x": self.snake[0]["x"] + dx,
                "y": self.snake[0]["y"] + dy}

    def danger(self, direction):
        head = self.next_head(direction)
        # Preserve the existing rule: the current tail is also an obstacle.
        return (not 0 <= head["x"] < self.GRID_W
                or not 0 <= head["y"] < self.GRID_H
                or head in self.snake)

    def step(self, direction):
        """Apply one move; return the reward and episode termination."""
        if self.game_over:
            return 0.0, True
        if self.danger(direction):
            self.game_over = True
            self.message = "GAME OVER : collision !"
            return -10.0, True
        self.direction = direction
        head = self.next_head(direction)
        self.snake.insert(0, head)
        self.steps_since_fruit += 1
        self.total_steps += 1
        if head == self.fruit:
            self.score += 1
            self.steps_since_fruit = 0
            self.fruit = self.generate_fruit()
            if self.fruit is None:
                self.game_over = True
                self.message = "Bravo : plateau rempli !"
            return 10.0, self.game_over
        self.snake.pop()
        return -0.01, False

    def generate_fruit(self):
        occupied = {(part["x"], part["y"]) for part in self.snake}
        free = [(x, y) for y in range(self.GRID_H)
                for x in range(self.GRID_W) if (x, y) not in occupied]
        if not free:
            return None
        x, y = self.rng.choice(free)
        return {"x": x, "y": y}
