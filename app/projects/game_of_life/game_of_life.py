import numpy as np

# TODO : Ajouter une fonctionnalité pour sauvegarder et charger des configurations spécifiques.
# TODO : add colors for live cells

class GameOfLife:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = np.random.choice([0, 1], size=(rows, cols))

    def step(self):
        new_grid = self.grid.copy()
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.count_neighbors(r, c)
                if self.grid[r, c] == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[r, c] = 0
                else:
                    if neighbors == 3:
                        new_grid[r, c] = 1
        self.grid = new_grid

    def count_neighbors(self, row, col):
        total = 0
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if (r == row and c == col) or r < 0 or c < 0 or r >= self.rows or c >= self.cols:
                    continue
                total += self.grid[r, c]
        return total
    
    def reset(self):
        self.grid = np.random.choice([0, 1], size=(self.rows, self.cols))

    def to_list(self):
        return self.grid.tolist()