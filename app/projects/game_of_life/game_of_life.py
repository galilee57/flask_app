import numpy as np

class GameOfLife:
    def __init__(self, rows, cols, random_init=True):
        self.rows = rows
        self.cols = cols
        if random_init:
            self.grid = np.random.choice([0, 1], size=(rows, cols)).astype(np.uint8)
        else:
            self.grid = np.zeros((rows, cols), dtype=np.uint8)

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
                total += int(self.grid[r, c])
        return total

    def reset(self):
        self.grid = np.random.choice([0, 1], size=(self.rows, self.cols)).astype(np.uint8)

    def clear(self):
        self.grid.fill(0)

    def to_list(self):
        return self.grid.tolist()

    def from_list(self, grid_list):
        arr = np.array(grid_list, dtype=np.uint8)
        if arr.ndim != 2:
            raise ValueError("grid_list must be 2D (list of lists)")
        self.rows, self.cols = arr.shape
        self.grid = arr