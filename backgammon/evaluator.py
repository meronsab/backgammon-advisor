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

# Weighted value of Red making each point (2+ checkers).
# Priority order: 5, 4, 7(bar), 20/21/18(anchors), 3, 2, 9, then others.
_RED_POINT_WEIGHTS = {
    5: 1.00, 4: 0.80, 7: 0.72,
    20: 0.70, 21: 0.65, 18: 0.62,
    3: 0.55, 2: 0.45, 9: 0.40,
    6: 0.35, 8: 0.28, 19: 0.48, 22: 0.42, 23: 0.32, 24: 0.20, 1: 0.22,
    10: 0.20, 11: 0.16, 12: 0.12, 13: 0.10,
}
_WHITE_POINT_WEIGHTS = {25 - p: w for p, w in _RED_POINT_WEIGHTS.items()}
_MAX_POINT_SCORE = sum(_RED_POINT_WEIGHTS.values())

def _home_score(board: Board) -> float:
    red = sum(w for p, w in _RED_POINT_WEIGHTS.items() if board.points[p] >= 2)
    white = sum(w for p, w in _WHITE_POINT_WEIGHTS.items() if board.points[p] <= -2)
    return (red - white) / _MAX_POINT_SCORE

def _hit_threat_score(board: Board) -> float:
    white_blots = [i for i in range(1, 25) if board.points[i] == -1]
    red_checkers = [i for i in range(1, 25) if board.points[i] > 0]
    threats = sum(1 for b in white_blots for r in red_checkers if 1 <= r - b <= 6)
    return min(threats / 5.0, 1.0)

def _gammon_danger(board: Board) -> float:
    """Penalty when opponent is bearing off while Red is still far behind."""
    white_off = board.white_off
    if white_off < 7:
        return 0.0
    red_pip = pip_count(board, 'red')
    if red_pip < 40:
        return 0.0
    return -(white_off / 15.0) * min(red_pip / 120.0, 1.0)

def _gammon_chance(board: Board) -> float:
    """Bonus when Red is bearing off while opponent is still far behind."""
    red_off = board.red_off
    if red_off < 7:
        return 0.0
    white_pip = pip_count(board, 'white')
    if white_pip < 40:
        return 0.0
    return (red_off / 15.0) * min(white_pip / 120.0, 1.0)

def evaluate(board: Board, plan: str = 'wise') -> float:
    w = PLAN_WEIGHTS[plan]
    score = (
        w['pip']   * _pip_score(board) +
        w['blot']  * _blot_score(board) +
        w['prime'] * _prime_score(board) +
        w['home']  * _home_score(board) +
        w['hit']   * _hit_threat_score(board) +
        0.15 * (_gammon_danger(board) + _gammon_chance(board))
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
