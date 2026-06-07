import math
from backgammon.board import Board, pip_count

PLAN_WEIGHTS = {
    'bold':    {'pip': 0.25, 'blot': 0.05, 'prime': 0.35, 'home': 0.20, 'hit': 0.15},
    'wise':    {'pip': 0.40, 'blot': 0.20, 'prime': 0.20, 'home': 0.15, 'hit': 0.05},
    'caution': {'pip': 0.50, 'blot': 0.35, 'prime': 0.10, 'home': 0.15, 'hit': -0.10},
}

def _pip_score(board: Board) -> float:
    red = pip_count(board, 'red')
    white = pip_count(board, 'white')
    return (white - red) / 167.0

def _blot_score(board: Board) -> float:
    red_blots = sum(1 for i in range(1, 25) if board.points[i] == 1)
    white_blots = sum(1 for i in range(1, 25) if board.points[i] == -1)
    return (white_blots - red_blots) / 8.0

def _prime_score(board: Board) -> float:
    def longest_prime(pts, positive):
        best = cur = 0
        for i in range(1, 25):
            if pts[i] != 0 and (pts[i] > 0) == positive:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        return best
    return (longest_prime(board.points, True) - longest_prime(board.points, False)) / 6.0

def _home_score(board: Board) -> float:
    red_home = sum(1 for i in range(1, 7) if board.points[i] >= 2)
    white_home = sum(1 for i in range(19, 25) if board.points[i] <= -2)
    return (red_home - white_home) / 6.0

def _hit_threat_score(board: Board) -> float:
    white_blots = [i for i in range(1, 25) if board.points[i] == -1]
    red_checkers = [i for i in range(1, 25) if board.points[i] > 0]
    threats = sum(1 for b in white_blots for r in red_checkers if 1 <= r - b <= 6)
    return min(threats / 5.0, 1.0)

def evaluate(board: Board, plan: str = 'wise') -> float:
    w = PLAN_WEIGHTS[plan]
    score = (
        w['pip']   * _pip_score(board) +
        w['blot']  * _blot_score(board) +
        w['prime'] * _prime_score(board) +
        w['home']  * _home_score(board) +
        w['hit']   * _hit_threat_score(board)
    )
    return max(-1.0, min(1.0, score))

def win_probability(score: float) -> dict:
    win = 1.0 / (1.0 + math.exp(-4.0 * score))
    gammon = max(0.0, (win - 0.5) * 0.55)
    backgammon = max(0.0, (win - 0.72) * 0.20)
    return {
        'win': round(win, 3),
        'gammon': round(gammon, 3),
        'backgammon': round(backgammon, 3),
    }

def cube_advice(win_pct: float) -> dict:
    if win_pct >= 0.85:
        return {'action': 'double', 'opponent_should': 'pass', 'note': 'Too good to take'}
    elif win_pct >= 0.70:
        return {'action': 'double', 'opponent_should': 'accept', 'note': 'Strong double'}
    elif win_pct >= 0.40:
        return {'action': 'hold', 'opponent_should': 'n/a', 'note': 'Not strong enough to double'}
    else:
        return {'action': 'beware', 'opponent_should': 'n/a', 'note': 'Consider accepting if opponent doubles'}
