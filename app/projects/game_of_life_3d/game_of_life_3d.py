from __future__ import annotations
import numpy as np
from itertools import product
from typing import Tuple, Iterable

# TODO : add buttons and slicers to change rules (B/S), torus mode, reset, etc.

class GameOfLife3D:
    """3D version of Conway's Game of Life with configurable rules (B/S)."""

    def __init__(
        self,
        shape: Tuple[int, int, int] = (48, 48, 48),
        rule_b: Iterable[int] = (4, 5),       # Birth conditions
        rule_s: Iterable[int] = (5, 6, 7, 8,),  # Survival conditions
        torus: bool = True,
        density: float = .05,
        seed: int | None = None,
    ) -> None:
        self.shape = tuple(shape)
        self.rule_b = set(rule_b)
        self.rule_s = set(rule_s)
        self.torus = torus
        self.rng = np.random.default_rng(seed)
        self.grid = self.rng.random(self.shape) <= density

    # -------------------------------------------------------------------------

    def reset(self, density: float | None = None, seed: int | None = None) -> None:
        """Reset the grid with a new random distribution."""
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        if density is None:
            density = np.mean(self.grid)
        self.grid = self.rng.random(self.shape) < float(density)

    # -------------------------------------------------------------------------

    def neighbors_count(self) -> np.ndarray:
        """Compute the number of alive neighbors for each cell in the 3D grid."""
        g = self.grid
        Z, Y, X = self.shape
        acc = np.zeros_like(g, dtype=np.uint8)

        for dz, dy, dx in product((-1, 0, 1), repeat=3):
            if (dz, dy, dx) == (0, 0, 0):
                continue

            if self.torus:
                # Torus behavior: wrap around using np.roll
                acc += np.roll(np.roll(np.roll(g, dz, axis=0), dy, axis=1), dx, axis=2)
            else:
                # Non-torus: zero padding at the borders
                z_src = slice(max(0, dz), Z + min(0, dz))
                y_src = slice(max(0, dy), Y + min(0, dy))
                x_src = slice(max(0, dx), X + min(0, dx))

                z_dst = slice(max(0, -dz), Z - max(0, dz))
                y_dst = slice(max(0, -dy), Y - max(0, dy))
                x_dst = slice(max(0, -dx), X - max(0, dx))

                acc[z_dst, y_dst, x_dst] += g[z_src, y_src, x_src]

        return acc

    # -------------------------------------------------------------------------

    def step(self) -> None:
        """Advance the simulation by one generation."""
        n_count = self.neighbors_count()
        alive = self.grid
        birth = (~alive) & np.isin(n_count, list(self.rule_b))
        survive = alive & np.isin(n_count, list(self.rule_s))
        self.grid = birth | survive

    # -------------------------------------------------------------------------

    def alive_coords(self) -> list[list[int]]:
        """Return a list of coordinates of alive cells."""
        return np.argwhere(self.grid).tolist()

    # -------------------------------------------------------------------------

    def config(self) -> dict:
        """Return the current configuration of the simulation."""
        return {
            "shape": list(self.shape),
            "rule_b": sorted(self.rule_b),
            "rule_s": sorted(self.rule_s),
            "torus": self.torus,
        }
