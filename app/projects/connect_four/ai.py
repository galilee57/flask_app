import math
import random

ROWS = 6
COLS = 7

def get_opponent(player):
    return 2 if player == 1 else 1

def get_valid_columns(grid):
    return [col for col in range(COLS) if grid[0][col]==0]

def play_move(grid, column, player):
    for row in range(ROWS - 1, -1, -1):
        if grid[row][column]==0:
            grid[row][column]=player
            return True
        
    return False

def simulate_move(grid, column, player):
    new_grid = [row[:] for row in grid]
    play_move(new_grid, column, player)
    return new_grid

def check_win(grid, player):
    # HORIZONTAL
    for row in range(ROWS):
        for col in range(COLS - 3):
            if (
                grid[row][col] == player
                and grid[row][col+1] == player
                and grid[row][col+2] == player
                and grid[row][col+3] == player
            ):
                return True
            
    # VERTICAL
    for row in range(ROWS - 3):
        for col in range(COLS):
            if(
                grid[row][col] == player
                and grid[row+1][col] == player
                and grid[row+2][col] == player
                and grid[row+3][col] == player
            ):
                return True
    
    # DIAGONALE DESCENDANTE
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if (
                grid[row][col] == player
                and grid[row + 1][col + 1] == player
                and grid[row + 2][col + 2] == player
                and grid[row + 3][col + 3] == player
            ):
                return True

    # DIAGONALE MONTANTE
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if (
                grid[row][col] == player
                and grid[row - 1][col + 1] == player
                and grid[row - 2][col + 2] == player
                and grid[row - 3][col + 3] == player
            ):
                return True

    return False

# On va parcourir une fenêtre de 4 cases et attribuer un score en fonction d'une heuristique simple
def score_position(grid, player):
    score = 0
    
    # Favoriser la colonne centrale
    center_column = [grid[row][COLS // 2] for row in range(ROWS)]
    score += center_column.count(player) * 3

    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = [grid[row][col + i] for i in range(4)]
            score += evaluate_window(window, player)

    # Vertical
    for col in range(COLS):
        for row in range(ROWS - 3):
            window = [grid[row + i][col] for i in range(4)]
            score += evaluate_window(window, player)

    # Diagonale descendante ↘
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [grid[row + i][col + i] for i in range(4)]
            score += evaluate_window(window, player)

    # Diagonale montante ↗
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [grid[row - i][col + i] for i in range(4)]
            score += evaluate_window(window, player)

    return score

# Heuristique pour évaluer une fenêtre de 4 cases
def evaluate_window(window, player):
    score = 0
    opponent = get_opponent(player)

    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(0) == 1:
        score += 10
    elif window.count(player) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent) == 3 and window.count(0) == 1:
        score -= 90

    return score

def minmax(grid, depth, alpha, beta, maximizing, ai_player):
    valid_columns = get_valid_columns(grid)
    opponent = get_opponent(ai_player)

    if check_win(grid, ai_player):
        return None, math.inf

    if check_win(grid, opponent):
        return None, -math.inf

    if depth == 0 or not valid_columns:
        return None, score_position(grid, ai_player)

    if maximizing:
        value = -math.inf
        best_column = random.choice(valid_columns)
        
        for column in valid_columns:
            new_grid = simulate_move(grid, column, ai_player)

            new_score = minmax(
                new_grid, 
                depth - 1, 
                alpha, 
                beta, 
                False, 
                ai_player
            )[1]

            if new_score > value:
                value = new_score
                best_column = column

            alpha = max(alpha, value)
            
            if alpha >= beta:
                break

        return best_column, value
    else:
        value = math.inf
        best_column = random.choice(valid_columns)

        for column in valid_columns:
            new_grid = simulate_move(grid, column, opponent)

            new_score = minmax(
                new_grid, 
                depth - 1, 
                alpha, 
                beta, 
                True, 
                ai_player
            )[1]

            if new_score < value:
                value = new_score
                best_column = column

            beta = min(beta, value)
            
            if alpha >= beta:
                break

        return best_column, value
    
def get_best_move(grid, player):
    column, _ = minmax(grid, 4, -math.inf, math.inf, True, player)
    return column