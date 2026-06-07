# Backgammon Advisor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Flask web app that advises the best backgammon move given the current board state, dice roll, and chosen game plan, with win probability, gammon odds, doubling cube advice, and a dice outcome histogram.

**Architecture:** Python Flask backend stores game state in the server session and exposes a JSON API. A single HTML page with vanilla JS calls the API and re-renders the board and advisor panel without page reloads. All move evaluation is pure Python heuristics — no external engine or AI API.

**Tech Stack:** Python 3.11+, Flask, pytest, vanilla JS/CSS, GitHub

---

## Board Convention (read before writing any code)

- Points 1–24 are absolute. **Red** (the user) moves 24 → 1. **White** (opponent) moves 1 → 24.
- `board.points[i]` for i in 1–24: positive = Red checkers, negative = White checkers, 0 = empty.
- `board.points[0]` is unused (padding so index == point number).
- Opening: Red on 24(×2), 13(×5), 8(×3), 6(×5). White on 1(×2), 12(×5), 17(×3), 19(×5).
- Red pip count = Σ(count × point) for Red pieces + red_bar × 25. White pip count = Σ(count × (25−point)) for White pieces + white_bar × 25.
- Red enters from bar at point `25 − die`. White enters from bar at point `die`.
- Red home board: points 1–6. White home board: points 19–24.
- Move notation: `"13/8 8/5"` → `[(13, 8), (8, 5)]`. Bar = `"bar"`, borne off = `"off"`.
- In code: from_point=0 → Red bar entry. to_point=0 → Red bears off. from_point=25 → White bar. to_point=25 → White bears off.

---

## File Map

```
backgammon-advisor/
├── CLAUDE.md
├── requirements.txt
├── pytest.ini
├── .gitignore
├── app.py                    # Flask app, session helpers, all API routes
├── backgammon/
│   ├── __init__.py
│   ├── board.py              # Board dataclass, opening position, pip count, move parsing, apply_move, generate_moves
│   ├── evaluator.py          # Position heuristics, win probability, cube advice
│   └── advisor.py            # best_move(), dice_histogram()
├── templates/
│   └── index.html            # Single-page UI: board, game plan tabs, advisor panel
├── static/
│   ├── style.css
│   └── app.js                # Board rendering, fetch calls, UI state
└── tests/
    ├── test_board.py
    ├── test_evaluator.py
    ├── test_advisor.py
    └── test_api.py
```

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`, `pytest.ini`, `.gitignore`, `CLAUDE.md`, `backgammon/__init__.py`

- [ ] **Step 1: Create virtualenv and install dependencies**

```bash
cd /home/meron/backgammon-advisor
python3 -m venv venv
source venv/bin/activate
pip install flask pytest
```

- [ ] **Step 2: Write requirements.txt**

```
flask>=3.0
pytest>=8.0
```

- [ ] **Step 3: Write pytest.ini**

```ini
[pytest]
testpaths = tests
```

- [ ] **Step 4: Write .gitignore**

```
venv/
__pycache__/
*.pyc
.env
*.egg-info/
.superpowers/
```

- [ ] **Step 5: Write CLAUDE.md**

```markdown
# Backgammon Advisor

Flask web app that advises the best move in backgammon using one-ply lookahead and heuristic evaluation.

## Running locally

```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python app.py        # visit http://localhost:5000
pytest               # run all tests
```

## Project layout

- `backgammon/board.py` — Board dataclass, move generation, move application
- `backgammon/evaluator.py` — Position heuristics and win probability
- `backgammon/advisor.py` — One-ply lookahead, histogram generation
- `app.py` — Flask routes and session management
- `templates/index.html` + `static/` — Single-page frontend

## Board convention

Red (you) moves from point 24 → 1. White (opponent) moves 1 → 24.
`board.points[i]` > 0 = Red, < 0 = White. Red home board = points 1–6.
Move notation: `"13/8 8/5"`. Bar entry: `"bar/19"`. Bear off: `"3/off"`.

## Heuristic weights (evaluator.py)

Three game plan modes shift weights: `PLAN_WEIGHTS` dict in `evaluator.py`.
Tune values there to change advisor aggressiveness.
```

- [ ] **Step 6: Create backgammon package**

```bash
mkdir -p backgammon tests
touch backgammon/__init__.py tests/__init__.py
```

- [ ] **Step 7: Commit**

```bash
git add requirements.txt pytest.ini .gitignore CLAUDE.md backgammon/__init__.py tests/__init__.py
git commit -m "feat: project setup, dependencies, CLAUDE.md"
```

---

## Task 2: Board Data Model

**Files:**
- Create: `backgammon/board.py`
- Create: `tests/test_board.py`

- [ ] **Step 1: Write failing tests for Board model**

```python
# tests/test_board.py
from backgammon.board import Board, opening_board, pip_count, parse_move

def test_opening_board_red_pip_count():
    b = opening_board()
    assert pip_count(b, 'red') == 167

def test_opening_board_white_pip_count():
    b = opening_board()
    assert pip_count(b, 'white') == 167

def test_opening_board_red_checkers():
    b = opening_board()
    assert b.points[24] == 2
    assert b.points[13] == 5
    assert b.points[8] == 3
    assert b.points[6] == 5

def test_opening_board_white_checkers():
    b = opening_board()
    assert b.points[1] == -2
    assert b.points[12] == -5
    assert b.points[17] == -3
    assert b.points[19] == -5

def test_opening_board_no_bar():
    b = opening_board()
    assert b.red_bar == 0
    assert b.white_bar == 0

def test_parse_move_normal():
    assert parse_move("13/8 8/5") == [(13, 8), (8, 5)]

def test_parse_move_bar_entry():
    assert parse_move("bar/19") == [(0, 19)]

def test_parse_move_bear_off():
    assert parse_move("3/off") == [(3, 0)]

def test_parse_move_single():
    assert parse_move("24/18") == [(24, 18)]
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
source venv/bin/activate && pytest tests/test_board.py -v
```

Expected: `ImportError` or `ModuleNotFoundError`.

- [ ] **Step 3: Implement Board model**

```python
# backgammon/board.py
from dataclasses import dataclass, field
from copy import deepcopy

@dataclass
class Board:
    points: list  # length 25; index 0 = padding, 1-24 = board points
    red_bar: int = 0
    white_bar: int = 0
    red_off: int = 0
    white_off: int = 0

    def copy(self):
        return Board(
            points=self.points[:],
            red_bar=self.red_bar,
            white_bar=self.white_bar,
            red_off=self.red_off,
            white_off=self.white_off,
        )

_OPENING = [0] * 25
_OPENING[24] = 2;  _OPENING[13] = 5;  _OPENING[8] = 3;  _OPENING[6] = 5
_OPENING[1] = -2;  _OPENING[12] = -5; _OPENING[17] = -3; _OPENING[19] = -5

def opening_board() -> Board:
    return Board(points=_OPENING[:])

def pip_count(board: Board, player: str) -> int:
    if player == 'red':
        total = sum(board.points[i] * i for i in range(1, 25) if board.points[i] > 0)
        return total + board.red_bar * 25
    else:
        total = sum((-board.points[i]) * (25 - i) for i in range(1, 25) if board.points[i] < 0)
        return total + board.white_bar * 25

def parse_move(notation: str) -> list:
    """Parse '13/8 8/5' into [(13,8),(8,5)]. 'bar'->0, 'off'->0 or 25."""
    result = []
    for part in notation.strip().split():
        src, dst = part.split('/')
        from_pt = 0 if src.lower() == 'bar' else int(src)
        to_pt = 0 if dst.lower() == 'off' else int(dst)
        result.append((from_pt, to_pt))
    return result

def board_to_dict(board: Board) -> dict:
    return {
        'points': board.points,
        'red_bar': board.red_bar,
        'white_bar': board.white_bar,
        'red_off': board.red_off,
        'white_off': board.white_off,
    }

def board_from_dict(d: dict) -> Board:
    return Board(
        points=d['points'],
        red_bar=d['red_bar'],
        white_bar=d['white_bar'],
        red_off=d['red_off'],
        white_off=d['white_off'],
    )
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_board.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backgammon/board.py tests/test_board.py
git commit -m "feat: board data model, opening position, pip count, move parsing"
```

---

## Task 3: Move Application

**Files:**
- Modify: `backgammon/board.py` (add `apply_move`, `is_blocked`)
- Modify: `tests/test_board.py` (add move application tests)

- [ ] **Step 1: Write failing tests**

```python
# append to tests/test_board.py
from backgammon.board import apply_move

def test_apply_normal_move_red():
    b = opening_board()
    new_b = apply_move(b, [(13, 8)], 'red')
    assert new_b.points[13] == 4   # one piece left
    assert new_b.points[8] == 4    # one added
    assert b.points[13] == 5       # original unchanged

def test_apply_move_hits_white_blot():
    b = opening_board()
    b.points[10] = -1  # white blot on point 10
    new_b = apply_move(b, [(13, 10)], 'red')
    assert new_b.points[10] == 1   # red now owns it
    assert new_b.white_bar == 1    # white piece sent to bar

def test_apply_bear_off_red():
    b = Board(points=[0]*25)
    b.points[3] = 2
    new_b = apply_move(b, [(3, 0)], 'red')
    assert new_b.points[3] == 1
    assert new_b.red_off == 1

def test_apply_bar_entry_red_empty_point():
    b = Board(points=[0]*25)
    b.red_bar = 1
    new_b = apply_move(b, [(0, 22)], 'red')  # bar/22, die=3
    assert new_b.red_bar == 0
    assert new_b.points[22] == 1

def test_apply_move_white():
    b = opening_board()
    new_b = apply_move(b, [(1, 7)], 'white')
    assert new_b.points[1] == -1
    assert new_b.points[7] == -1
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_board.py::test_apply_normal_move_red -v
```

Expected: `ImportError` for `apply_move`.

- [ ] **Step 3: Implement apply_move and is_blocked**

```python
# append to backgammon/board.py

def is_blocked(board: Board, point: int, player: str) -> bool:
    """True if `player` cannot land on `point` (opponent has 2+ checkers there)."""
    if player == 'red':
        return board.points[point] <= -2
    else:
        return board.points[point] >= 2

def apply_move(board: Board, move: list, player: str) -> Board:
    """Return new Board with move applied. move = list of (from_pt, to_pt)."""
    b = board.copy()
    for from_pt, to_pt in move:
        if player == 'red':
            # Remove from source
            if from_pt == 0:   # from bar
                b.red_bar -= 1
            else:
                b.points[from_pt] -= 1
            # Place at destination
            if to_pt == 0:     # bear off
                b.red_off += 1
            else:
                if b.points[to_pt] == -1:   # hit white blot
                    b.points[to_pt] = 0
                    b.white_bar += 1
                b.points[to_pt] += 1
        else:  # white
            if from_pt == 25:  # from bar
                b.white_bar -= 1
            else:
                b.points[from_pt] += 1   # remove white (less negative)
            if to_pt == 25:    # bear off
                b.white_off += 1
            else:
                if b.points[to_pt] == 1:   # hit red blot
                    b.points[to_pt] = 0
                    b.red_bar += 1
                b.points[to_pt] -= 1
    return b
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_board.py -v
```

Expected: all tests PASS (skip/remove the invalid bar test from step 1).

- [ ] **Step 6: Commit**

```bash
git add backgammon/board.py tests/test_board.py
git commit -m "feat: move application with hit detection and bear-off"
```

---

## Task 4: Legal Move Generation

**Files:**
- Modify: `backgammon/board.py` (add `generate_moves`, helpers)
- Modify: `tests/test_board.py` (add move generation tests)

- [ ] **Step 1: Write failing tests**

```python
# append to tests/test_board.py
from backgammon.board import generate_moves, all_home

def test_all_home_red_false_at_opening():
    b = opening_board()
    assert all_home(b, 'red') is False

def test_all_home_red_true():
    b = Board(points=[0]*25)
    b.points[3] = 3; b.points[5] = 2
    assert all_home(b, 'red') is True

def test_generate_moves_returns_list():
    b = opening_board()
    moves = generate_moves(b, [6, 1], 'red')
    assert isinstance(moves, list)
    assert len(moves) > 0

def test_generate_moves_uses_both_dice():
    b = opening_board()
    moves = generate_moves(b, [6, 1], 'red')
    # Every move should use 2 dice (2 sub-moves) when possible
    assert all(len(m) == 2 for m in moves)

def test_generate_doubles_four_moves():
    b = opening_board()
    moves = generate_moves(b, [3, 3, 3, 3], 'red')
    assert all(len(m) == 4 for m in moves)

def test_generate_moves_bar_first():
    b = opening_board()
    b.red_bar = 1
    moves = generate_moves(b, [6, 1], 'red')
    # All moves must start with a bar entry
    assert all(m[0][0] == 0 for m in moves)

def test_generate_moves_no_landing_on_blocked():
    b = Board(points=[0]*25)
    b.points[24] = 2; b.points[20] = -2  # point 20 blocked by white
    moves = generate_moves(b, [4, 1], 'red')
    for m in moves:
        for _, to_pt in m:
            assert to_pt != 20
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_board.py -k "generate" -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement generate_moves**

```python
# append to backgammon/board.py
from itertools import permutations as _perms

def all_home(board: Board, player: str) -> bool:
    if player == 'red':
        if board.red_bar > 0:
            return False
        return all(board.points[i] <= 0 for i in range(7, 25))
    else:
        if board.white_bar > 0:
            return False
        return all(board.points[i] >= 0 for i in range(1, 19))

def _can_move_one(board: Board, from_pt: int, die: int, player: str):
    """Return to_point if this single checker move is legal, else None."""
    if player == 'red':
        if from_pt == 0:           # from bar
            to_pt = 25 - die
            if 19 <= to_pt <= 24 and not is_blocked(board, to_pt, 'red'):
                return to_pt
            return None
        to_pt = from_pt - die
        if to_pt >= 1:
            if not is_blocked(board, to_pt, 'red'):
                return to_pt
            return None
        # Bearing off
        if all_home(board, 'red'):
            if to_pt == 0:         # exact
                return 0
            if to_pt < 0:          # overshoot — only if no higher checker
                highest = max((i for i in range(from_pt + 1, 7) if board.points[i] > 0), default=None)
                if highest is None:
                    return 0
        return None
    else:  # white
        if from_pt == 25:          # from bar
            to_pt = die
            if 1 <= to_pt <= 6 and not is_blocked(board, to_pt, 'white'):
                return to_pt
            return None
        to_pt = from_pt + die
        if to_pt <= 24:
            if not is_blocked(board, to_pt, 'white'):
                return to_pt
            return None
        if all_home(board, 'white'):
            if to_pt == 25:
                return 25
            lowest = min((i for i in range(19, from_pt) if board.points[i] < 0), default=None)
            if lowest is None:
                return 25
        return None

def _checker_positions(board: Board, player: str) -> list:
    if player == 'red':
        pts = [0] * board.red_bar + [i for i in range(1, 25) for _ in range(board.points[i]) if board.points[i] > 0]
    else:
        pts = [25] * board.white_bar + [i for i in range(1, 25) for _ in range(-board.points[i]) if board.points[i] < 0]
    return pts

def _gen_recursive(board: Board, dice: list, player: str, move_so_far: list, results: set):
    if not dice:
        results.add(tuple(move_so_far))
        return
    tried = set()
    checkers = set(_checker_positions(board, player))
    moved = False
    for from_pt in checkers:
        for die in set(dice):
            if (from_pt, die) in tried:
                continue
            tried.add((from_pt, die))
            to_pt = _can_move_one(board, from_pt, die, player)
            if to_pt is not None:
                new_dice = dice[:]
                new_dice.remove(die)
                new_board = apply_move(board, [(from_pt, to_pt)], player)
                _gen_recursive(new_board, new_dice, player, move_so_far + [(from_pt, to_pt)], results)
                moved = True
    if not moved:
        results.add(tuple(move_so_far))

def generate_moves(board: Board, dice: list, player: str) -> list:
    """Return list of legal move sequences. Each move = list of (from, to) tuples."""
    raw = set()
    _gen_recursive(board, dice[:], player, [], raw)
    if not raw:
        return [[]]
    # Must use maximum number of dice possible
    max_len = max(len(m) for m in raw)
    # Filter to max-length moves only
    best = [list(m) for m in raw if len(m) == max_len]
    # If max_len == 1, prefer higher die (backgammon rule)
    if max_len == 1 and len(dice) == 2:
        max_die_used = max(abs(m[0][0] - m[0][1]) for m in best if m)
        best = [m for m in best if m and abs(m[0][0] - m[0][1]) == max_die_used]
    # Deduplicate by frozenset of moves (order doesn't matter)
    seen = set()
    deduped = []
    for m in best:
        key = frozenset(m)
        if key not in seen:
            seen.add(key)
            deduped.append(m)
    return deduped
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_board.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backgammon/board.py tests/test_board.py
git commit -m "feat: legal move generation with bar, bear-off, max-dice rule"
```

---

## Task 5: Position Evaluator

**Files:**
- Create: `backgammon/evaluator.py`
- Create: `tests/test_evaluator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_evaluator.py
from backgammon.board import opening_board, Board
from backgammon.evaluator import evaluate, PLAN_WEIGHTS

def test_evaluate_opening_near_zero():
    b = opening_board()
    score = evaluate(b, 'wise')
    # Symmetric opening position should be close to 0
    assert -0.1 < score < 0.1

def test_evaluate_returns_float():
    b = opening_board()
    assert isinstance(evaluate(b, 'wise'), float)

def test_evaluate_red_ahead_positive():
    b = Board(points=[0]*25)
    # Red has all checkers home, opponent far away
    b.points[3] = 5; b.points[4] = 5; b.points[5] = 5
    b.points[20] = -15
    score = evaluate(b, 'wise')
    assert score > 0.3

def test_evaluate_white_ahead_negative():
    b = Board(points=[0]*25)
    b.points[22] = -5; b.points[21] = -5; b.points[20] = -5
    b.points[5] = 15
    score = evaluate(b, 'wise')
    assert score < -0.3

def test_plan_weights_keys():
    assert set(PLAN_WEIGHTS.keys()) == {'bold', 'wise', 'caution'}
    for plan in PLAN_WEIGHTS.values():
        assert 'pip' in plan
        assert 'blot' in plan
        assert 'prime' in plan
        assert 'home' in plan
        assert 'hit' in plan
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_evaluator.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement evaluator**

```python
# backgammon/evaluator.py
from backgammon.board import Board, pip_count

PLAN_WEIGHTS = {
    'bold':    {'pip': 0.25, 'blot': 0.05, 'prime': 0.35, 'home': 0.20, 'hit': 0.15},
    'wise':    {'pip': 0.40, 'blot': 0.20, 'prime': 0.20, 'home': 0.15, 'hit': 0.05},
    'caution': {'pip': 0.50, 'blot': 0.35, 'prime': 0.10, 'home': 0.15, 'hit': -0.10},
}

def _pip_score(board: Board) -> float:
    """Positive when Red is ahead in pip race."""
    red = pip_count(board, 'red')
    white = pip_count(board, 'white')
    max_pip = 167  # opening pip count
    return (white - red) / max_pip

def _blot_score(board: Board) -> float:
    """Negative when Red has exposed blots (isolated single checkers)."""
    red_blots = sum(1 for i in range(1, 25) if board.points[i] == 1)
    white_blots = sum(1 for i in range(1, 25) if board.points[i] == -1)
    return (white_blots - red_blots) / 8.0

def _prime_score(board: Board) -> float:
    """Positive when Red has consecutive blocked points (primes)."""
    def longest_prime(pts, sign):
        best = cur = 0
        for i in range(1, 25):
            if (pts[i] > 0) == sign and pts[i] != 0:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        return best
    red_prime = longest_prime(board.points, True)
    white_prime = longest_prime(board.points, False)
    return (red_prime - white_prime) / 6.0

def _home_score(board: Board) -> float:
    """Positive when Red has strong home board (points made in 1-6)."""
    red_home = sum(1 for i in range(1, 7) if board.points[i] >= 2)
    white_home = sum(1 for i in range(19, 25) if board.points[i] <= -2)
    return (red_home - white_home) / 6.0

def _hit_threat_score(board: Board) -> float:
    """Positive when Red can threaten opponent blots."""
    white_blots = [i for i in range(1, 25) if board.points[i] == -1]
    red_checkers = [i for i in range(1, 25) if board.points[i] > 0]
    threats = 0
    for blot in white_blots:
        for checker in red_checkers:
            dist = checker - blot
            if 1 <= dist <= 6:
                threats += 1
    return min(threats / 5.0, 1.0)

def evaluate(board: Board, plan: str = 'wise') -> float:
    """Score position from Red's perspective. Positive = good for Red."""
    w = PLAN_WEIGHTS[plan]
    score = (
        w['pip']  * _pip_score(board) +
        w['blot'] * _blot_score(board) +
        w['prime'] * _prime_score(board) +
        w['home'] * _home_score(board) +
        w['hit']  * _hit_threat_score(board)
    )
    return max(-1.0, min(1.0, score))
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_evaluator.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backgammon/evaluator.py tests/test_evaluator.py
git commit -m "feat: position evaluator with bold/wise/caution game plans"
```

---

## Task 6: Win Probability and Cube Advice

**Files:**
- Modify: `backgammon/evaluator.py`
- Modify: `tests/test_evaluator.py`

- [ ] **Step 1: Write failing tests**

```python
# append to tests/test_evaluator.py
from backgammon.evaluator import win_probability, cube_advice

def test_win_probability_symmetric():
    probs = win_probability(0.0)
    assert 0.48 < probs['win'] < 0.52

def test_win_probability_strong_red():
    probs = win_probability(0.8)
    assert probs['win'] > 0.85
    assert probs['gammon'] > 0.15
    assert probs['backgammon'] >= 0.0

def test_win_probability_keys():
    probs = win_probability(0.0)
    assert set(probs.keys()) == {'win', 'gammon', 'backgammon'}

def test_cube_advice_double():
    advice = cube_advice(0.73)
    assert advice['action'] == 'double'

def test_cube_advice_no_action():
    advice = cube_advice(0.55)
    assert advice['action'] == 'hold'

def test_cube_advice_accept():
    # From opponent's view: if red win% is 70%, opponent should accept (their win% = 30% > 25%)
    advice = cube_advice(0.70)
    assert advice['opponent_should'] == 'accept'

def test_cube_advice_pass():
    advice = cube_advice(0.87)
    assert advice['opponent_should'] == 'pass'
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_evaluator.py -k "win_probability or cube_advice" -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement win_probability and cube_advice**

```python
# append to backgammon/evaluator.py
import math

def win_probability(score: float) -> dict:
    """Derive Win%, Gammon%, Backgammon% from heuristic score."""
    win = 1.0 / (1.0 + math.exp(-4.0 * score))
    gammon = max(0.0, (win - 0.5) * 0.55)
    backgammon = max(0.0, (win - 0.72) * 0.20)
    return {
        'win': round(win, 3),
        'gammon': round(gammon, 3),
        'backgammon': round(backgammon, 3),
    }

def cube_advice(win_pct: float) -> dict:
    """Advise on doubling cube. win_pct = Red's win probability (0-1)."""
    opp_win = 1.0 - win_pct
    if win_pct >= 0.85:
        action = 'double'
        opponent_should = 'pass'
        note = 'Too good to take — opponent should drop'
    elif win_pct >= 0.70:
        action = 'double'
        opponent_should = 'accept'
        note = 'Strong double — opponent is near take/pass boundary'
    elif win_pct >= 0.40:
        action = 'hold'
        opponent_should = 'n/a'
        note = 'No double yet — position not strong enough'
    else:
        action = 'beware'
        opponent_should = 'n/a'
        note = 'Consider accepting if opponent doubles'
    return {'action': action, 'opponent_should': opponent_should, 'note': note}
```

- [ ] **Step 4: Run all evaluator tests**

```bash
pytest tests/test_evaluator.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backgammon/evaluator.py tests/test_evaluator.py
git commit -m "feat: win probability and cube advice from heuristic score"
```

---

## Task 7: Advisor (Best Move + Histogram)

**Files:**
- Create: `backgammon/advisor.py`
- Create: `tests/test_advisor.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_advisor.py
from backgammon.board import opening_board
from backgammon.advisor import best_move, dice_histogram, ALL_DICE_COMBOS

def test_all_dice_combos_count():
    assert len(ALL_DICE_COMBOS) == 21

def test_all_dice_combos_probabilities_sum():
    total = sum(prob for _, prob in ALL_DICE_COMBOS)
    assert abs(total - 1.0) < 0.001

def test_best_move_returns_list():
    b = opening_board()
    move = best_move(b, [6, 1], 'wise')
    assert isinstance(move, list)
    assert len(move) > 0

def test_best_move_is_legal():
    from backgammon.board import generate_moves
    b = opening_board()
    move = best_move(b, [3, 1], 'wise')
    legal = generate_moves(b, [3, 1], 'red')
    assert move in legal

def test_dice_histogram_returns_21_entries():
    b = opening_board()
    hist = dice_histogram(b, 'wise')
    assert len(hist) == 21

def test_dice_histogram_has_required_keys():
    b = opening_board()
    hist = dice_histogram(b, 'wise')
    entry = hist[0]
    assert 'dice' in entry
    assert 'score' in entry
    assert 'prob' in entry
    assert 'best_move' in entry

def test_dice_histogram_sorted_descending():
    b = opening_board()
    hist = dice_histogram(b, 'wise')
    scores = [e['score'] for e in hist]
    assert scores == sorted(scores, reverse=True)
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_advisor.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement advisor**

```python
# backgammon/advisor.py
from backgammon.board import Board, generate_moves, apply_move
from backgammon.evaluator import evaluate

# All 21 unique dice combinations with their probabilities
# Doubles have prob 1/36, non-doubles have prob 2/36
ALL_DICE_COMBOS = []
for d1 in range(1, 7):
    for d2 in range(d1, 7):
        dice = [d1, d2, d1, d2] if d1 == d2 else [d1, d2]
        prob = (1/36) if d1 == d2 else (2/36)
        ALL_DICE_COMBOS.append((dice, prob))

def _score_move(board: Board, move: list, plan: str) -> float:
    """Score a Red move using 1-ply lookahead over all opponent responses."""
    new_board = apply_move(board, move, 'red')
    expected = 0.0
    for opp_dice, prob in ALL_DICE_COMBOS:
        opp_moves = generate_moves(new_board, opp_dice, 'white')
        if not opp_moves or opp_moves == [[]]:
            expected += prob * evaluate(new_board, plan)
        else:
            # Opponent picks the move that minimizes Red's score
            worst = min(
                evaluate(apply_move(new_board, m, 'white'), plan)
                for m in opp_moves
            )
            expected += prob * worst
    return expected

def best_move(board: Board, dice: list, plan: str = 'wise') -> list:
    """Return the best legal move for Red given dice and game plan."""
    moves = generate_moves(board, dice, 'red')
    if not moves or moves == [[]]:
        return []
    return max(moves, key=lambda m: _score_move(board, m, plan))

def dice_histogram(board: Board, plan: str = 'wise') -> list:
    """Return all 21 dice outcomes scored, sorted best to worst."""
    results = []
    for dice, prob in ALL_DICE_COMBOS:
        move = best_move(board, dice, plan)
        if move:
            new_board = apply_move(board, move, 'red')
            score = evaluate(new_board, plan)
        else:
            score = evaluate(board, plan)
        move_str = ' '.join(f'{f}/{"off" if t==0 else t}' for f, t in move) if move else '—'
        results.append({
            'dice': dice[:2] if dice[0] == dice[1] else dice,
            'score': round(score, 3),
            'prob': round(prob, 4),
            'best_move': move_str,
        })
    return sorted(results, key=lambda x: x['score'], reverse=True)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_advisor.py -v
```

Expected: all 7 tests PASS. (Note: `best_move` may take a few seconds — this is expected for 1-ply lookahead.)

- [ ] **Step 5: Commit**

```bash
git add backgammon/advisor.py tests/test_advisor.py
git commit -m "feat: 1-ply lookahead best_move and dice_histogram"
```

---

## Task 8: Flask App and API Endpoints

**Files:**
- Create: `app.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_api.py
import pytest
import json
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test'
    with app.test_client() as c:
        yield c

def test_new_game(client):
    resp = client.post('/api/new-game')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'board' in data
    assert data['board']['red_bar'] == 0

def test_get_state_after_new_game(client):
    client.post('/api/new-game')
    resp = client.get('/api/state')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'board' in data
    assert 'analysis' in data

def test_advise(client):
    client.post('/api/new-game')
    resp = client.post('/api/advise', json={'dice': [6, 1], 'plan': 'wise'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'best_move' in data
    assert 'histogram' in data
    assert 'analysis' in data

def test_apply_move(client):
    client.post('/api/new-game')
    resp = client.post('/api/apply-move', json={'move': '13/7 8/7'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'board' in data

def test_opponent_move(client):
    client.post('/api/new-game')
    resp = client.post('/api/opponent-move', json={'dice': [3, 1], 'move': '8/5 6/5'})
    assert resp.status_code == 200

def test_get_state_no_session_returns_400(client):
    resp = client.get('/api/state')
    assert resp.status_code == 400
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_api.py -v
```

Expected: `ImportError` or `ModuleNotFoundError`.

- [ ] **Step 3: Implement app.py**

```python
# app.py
from flask import Flask, request, jsonify, session, render_template
from backgammon.board import (
    opening_board, board_to_dict, board_from_dict, parse_move, apply_move
)
from backgammon.evaluator import evaluate, win_probability, cube_advice
from backgammon.advisor import best_move, dice_histogram

def create_app():
    app = Flask(__name__)
    app.secret_key = 'change-me-in-production'

    def _analysis(board):
        score = evaluate(board)
        probs = win_probability(score)
        cube = cube_advice(probs['win'])
        return {
            'score': round(score, 3),
            'win_pct': round(probs['win'] * 100, 1),
            'gammon_pct': round(probs['gammon'] * 100, 1),
            'backgammon_pct': round(probs['backgammon'] * 100, 1),
            'cube': cube,
        }

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.post('/api/new-game')
    def new_game():
        b = opening_board()
        session['board'] = board_to_dict(b)
        session['history'] = []
        return jsonify({'board': board_to_dict(b), 'analysis': _analysis(b)})

    @app.get('/api/state')
    def state():
        if 'board' not in session:
            return jsonify({'error': 'No active game'}), 400
        b = board_from_dict(session['board'])
        return jsonify({
            'board': board_to_dict(b),
            'analysis': _analysis(b),
            'history': session.get('history', []),
        })

    @app.post('/api/advise')
    def advise():
        if 'board' not in session:
            return jsonify({'error': 'No active game'}), 400
        data = request.get_json()
        dice = data['dice']
        plan = data.get('plan', 'wise')
        b = board_from_dict(session['board'])
        move = best_move(b, dice, plan)
        hist = dice_histogram(b, plan)
        move_str = ' '.join(f'{f}/{"off" if t==0 else t}' for f, t in move) if move else '—'
        new_b = apply_move(b, move, 'red') if move else b
        return jsonify({
            'best_move': move_str,
            'histogram': hist,
            'analysis': _analysis(new_b),
        })

    @app.post('/api/apply-move')
    def apply_move_route():
        if 'board' not in session:
            return jsonify({'error': 'No active game'}), 400
        data = request.get_json()
        b = board_from_dict(session['board'])
        move = parse_move(data['move'])
        new_b = apply_move(b, move, 'red')
        session['board'] = board_to_dict(new_b)
        history = session.get('history', [])
        history.append({'player': 'you', 'move': data['move']})
        session['history'] = history
        return jsonify({'board': board_to_dict(new_b), 'analysis': _analysis(new_b)})

    @app.post('/api/opponent-move')
    def opponent_move():
        if 'board' not in session:
            return jsonify({'error': 'No active game'}), 400
        data = request.get_json()
        b = board_from_dict(session['board'])
        move = parse_move(data['move'])
        new_b = apply_move(b, move, 'white')
        session['board'] = board_to_dict(new_b)
        history = session.get('history', [])
        history.append({'player': 'opp', 'dice': data.get('dice', []), 'move': data['move']})
        session['history'] = history
        return jsonify({'board': board_to_dict(new_b), 'analysis': _analysis(new_b)})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_api.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_api.py
git commit -m "feat: Flask app with all API endpoints and session management"
```

---

## Task 9: Frontend HTML and CSS

**Files:**
- Create: `templates/index.html`
- Create: `static/style.css`

- [ ] **Step 1: Create static directory**

```bash
mkdir -p static templates
```

- [ ] **Step 2: Write style.css**

```css
/* static/style.css */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0f0f1a; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 13px; display: flex; flex-direction: column; min-height: 100vh; }
header { background: #1a1a2e; padding: 10px 20px; display: flex; align-items: center; gap: 16px; border-bottom: 1px solid #2a2a3e; }
header h1 { font-size: 16px; font-weight: 600; color: #fff; }

/* Plan tabs */
.plan-tabs { display: flex; gap: 6px; }
.plan-tab { padding: 5px 14px; border-radius: 20px; border: 1px solid #444; cursor: pointer; font-size: 12px; font-weight: 600; transition: all .15s; }
.plan-tab[data-plan="bold"]    { color: #e74c3c; border-color: #e74c3c; }
.plan-tab[data-plan="wise"]    { color: #3498db; border-color: #3498db; }
.plan-tab[data-plan="caution"] { color: #2ecc71; border-color: #2ecc71; }
.plan-tab.active { color: #fff; }
.plan-tab[data-plan="bold"].active    { background: #e74c3c; }
.plan-tab[data-plan="wise"].active    { background: #3498db; }
.plan-tab[data-plan="caution"].active { background: #2ecc71; }

/* Layout */
main { display: grid; grid-template-columns: 1fr 300px; gap: 14px; padding: 14px; flex: 1; }

/* Board */
.board-section { display: flex; flex-direction: column; gap: 10px; }
.board-outer { background: #8B4513; border: 5px solid #5c2d0a; border-radius: 8px; padding: 8px; }
.board-inner { background: #2d8a4e; border-radius: 4px; position: relative; height: 260px; display: grid; grid-template-rows: 1fr 16px 1fr; overflow: hidden; }
.board-bar { position: absolute; left: 50%; transform: translateX(-50%); width: 24px; height: 100%; background: #8B4513; z-index: 2; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 8px; color: #c8a96e; gap: 4px; }
.points-row { display: flex; padding: 0 30px; gap: 3px; position: relative; }
.point { flex: 1; display: flex; flex-direction: column; align-items: center; position: relative; min-width: 0; }
.point-triangle { position: absolute; width: 100%; height: 100px; pointer-events: none; }
.top-row .point-triangle { top: 0; clip-path: polygon(50% 100%, 0 0, 100% 0); }
.bot-row .point-triangle { bottom: 0; clip-path: polygon(50% 0, 0 100%, 100% 100%); }
.tri-dark  { background: #8B1a1a; }
.tri-light { background: #e8d5a0; }
.checker { width: 18px; height: 18px; border-radius: 50%; border: 2px solid rgba(0,0,0,0.35); position: relative; z-index: 1; flex-shrink: 0; }
.checker.red   { background: radial-gradient(circle at 35% 35%, #e74c3c, #922b21); }
.checker.white { background: radial-gradient(circle at 35% 35%, #f5f5f5, #aaa); }
.board-mid { background: #1a6e36; display: flex; align-items: center; justify-content: center; font-size: 9px; color: rgba(255,255,255,0.15); letter-spacing: 2px; }
.point-labels { display: flex; padding: 2px 30px; gap: 3px; font-size: 9px; color: rgba(255,255,255,0.4); }
.point-labels span { flex: 1; text-align: center; }
.point-labels .bar-space { width: 24px; flex: none; }
.pip-row { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; padding: 4px 2px; }

/* Move history */
.history { background: #12121e; border-radius: 8px; padding: 10px; font-family: monospace; font-size: 11px; color: #666; max-height: 120px; overflow-y: auto; }
.history-entry.you { color: #e74c3c; }
.history-entry.opp { color: #bbb; }

/* Right panel */
.panel { display: flex; flex-direction: column; gap: 10px; }
.card { background: #1e1e2e; border-radius: 8px; padding: 12px; }
.card-title { font-size: 10px; color: #555; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }

/* Win stats */
.win-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
.stat-box { background: #12121e; border-radius: 6px; padding: 8px 4px; text-align: center; }
.stat-val { font-size: 17px; font-weight: 700; }
.stat-label { font-size: 9px; color: #555; margin-top: 2px; }
.green { color: #2ecc71; } .yellow { color: #f1c40f; } .blue { color: #3498db; }

/* Cube advice */
.cube-box { margin-top: 8px; padding: 8px 10px; border-radius: 6px; border: 1px solid #444; display: flex; justify-content: space-between; align-items: center; }
.cube-box.double { background: #2a1e0a; border-color: #f39c12; }
.cube-box.hold   { background: #0a1a10; border-color: #2ecc71; }
.cube-box.beware { background: #1a1a2e; border-color: #666; }
.cube-action { font-size: 13px; font-weight: 700; }
.cube-box.double .cube-action { color: #f39c12; }
.cube-box.hold   .cube-action { color: #2ecc71; }
.cube-opp { font-size: 10px; color: #888; }

/* Advice card */
.best-move-box { background: #1a3a2e; border: 1px solid #2ecc71; border-radius: 6px; padding: 10px; }
.move-notation { font-size: 18px; font-weight: 700; font-family: monospace; color: #fff; }
.move-score { font-size: 11px; color: #aaa; margin-top: 3px; }
.btn-row { display: flex; gap: 6px; margin-top: 8px; }
.btn { flex: 1; padding: 7px; border-radius: 6px; border: none; font-size: 12px; font-weight: 600; cursor: pointer; }
.btn-take { background: #2ecc71; color: #0a1a10; }
.btn-override { background: #1e1e2e; border: 1px solid #555; color: #aaa; }
.override-input { display: none; margin-top: 8px; }
.override-input.visible { display: block; }
.override-input input { width: 100%; background: #12121e; border: 1px solid #555; border-radius: 6px; padding: 6px 8px; color: #fff; font-size: 12px; font-family: monospace; }

/* Dice input */
.dice-row { display: flex; gap: 8px; align-items: center; }
.dice-input { background: #12121e; border: 1px solid #555; border-radius: 6px; padding: 6px 8px; color: #fff; font-size: 13px; width: 60px; text-align: center; }
.get-advice-btn { flex: 1; background: #3498db; color: #fff; }

/* Histogram */
.hist-entry { display: flex; align-items: center; gap: 5px; margin-bottom: 4px; }
.hist-dice { font-size: 10px; color: #888; width: 24px; flex-shrink: 0; font-family: monospace; }
.hist-bar-bg { flex: 1; background: #12121e; border-radius: 2px; height: 10px; overflow: hidden; }
.hist-bar { height: 100%; border-radius: 2px; transition: width .3s; }
.hist-val { font-size: 10px; width: 38px; text-align: right; flex-shrink: 0; font-family: monospace; }
.bar-pos { background: #2ecc71; }
.bar-neu { background: #f39c12; }
.bar-neg { background: #e74c3c; }

/* Opponent turn */
.opp-inputs { display: flex; gap: 6px; }
.opp-inputs input { background: #12121e; border: 1px solid #444; border-radius: 6px; padding: 6px 8px; color: #fff; font-size: 12px; }
.opp-dice-input { width: 60px; }
.opp-move-input { flex: 1; font-family: monospace; }
.next-btn { width: 100%; margin-top: 6px; background: #e74c3c; color: #fff; }
```

- [ ] **Step 3: Write index.html**

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Backgammon Advisor</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <h1>Backgammon Advisor</h1>
  <div class="plan-tabs">
    <button class="plan-tab" data-plan="bold">⚔️ Bold</button>
    <button class="plan-tab active" data-plan="wise">🎯 Wise</button>
    <button class="plan-tab" data-plan="caution">🛡️ Caution</button>
  </div>
  <button class="btn" style="background:#333;color:#aaa;margin-left:auto;" id="new-game-btn">New Game</button>
</header>

<main>
  <div class="board-section">
    <!-- Top point labels: 13–24 -->
    <div class="point-labels" id="labels-top">
      <span>13</span><span>14</span><span>15</span><span>16</span><span>17</span><span>18</span>
      <span class="bar-space"></span>
      <span>19</span><span>20</span><span>21</span><span>22</span><span>23</span><span>24</span>
    </div>

    <div class="board-outer">
      <div class="board-inner" id="board">
        <div class="board-bar">BAR<br><span id="bar-red">0</span>/<span id="bar-white">0</span></div>
        <!-- Top row (points 13–24, opponent direction) -->
        <div class="points-row top-row" id="top-row"></div>
        <div class="board-mid">· · · · · · · · · · · ·</div>
        <!-- Bottom row (points 12–1, your direction) -->
        <div class="points-row bot-row" id="bot-row"></div>
      </div>
    </div>

    <!-- Bottom point labels: 12–1 -->
    <div class="point-labels" id="labels-bot">
      <span>12</span><span>11</span><span>10</span><span>9</span><span>8</span><span>7</span>
      <span class="bar-space"></span>
      <span>6</span><span>5</span><span>4</span><span>3</span><span>2</span><span>1</span>
    </div>

    <div class="pip-row">
      <span>🔴 You · Pip: <b id="pip-red">—</b></span>
      <span>⚪ Opp · Pip: <b id="pip-white">—</b></span>
    </div>

    <div class="history" id="history-log"><em style="color:#444">Move history will appear here.</em></div>
  </div>

  <!-- Right panel -->
  <div class="panel">

    <!-- Win probabilities -->
    <div class="card">
      <div class="card-title">Position Analysis</div>
      <div class="win-stats">
        <div class="stat-box"><div class="stat-val green" id="win-pct">—</div><div class="stat-label">Win %</div></div>
        <div class="stat-box"><div class="stat-val yellow" id="gammon-pct">—</div><div class="stat-label">Gammon %</div></div>
        <div class="stat-box"><div class="stat-val blue" id="bg-pct">—</div><div class="stat-label">BG %</div></div>
      </div>
      <div class="cube-box hold" id="cube-box">
        <div>
          <div style="font-size:10px;color:#888;">Doubling cube</div>
          <div class="cube-action" id="cube-action">—</div>
        </div>
        <div class="cube-opp" id="cube-opp"></div>
      </div>
    </div>

    <!-- Dice input + advice -->
    <div class="card">
      <div class="card-title">Your Roll</div>
      <div class="dice-row">
        <input class="dice-input" id="die1" type="number" min="1" max="6" placeholder="d1">
        <input class="dice-input" id="die2" type="number" min="1" max="6" placeholder="d2">
        <button class="btn get-advice-btn" id="advise-btn">Get Advice</button>
      </div>
      <!-- Advice result (hidden until advice fetched) -->
      <div id="advice-result" style="display:none;margin-top:10px;">
        <div class="best-move-box">
          <div class="move-notation" id="best-move-text">—</div>
          <div class="move-score" id="best-move-score"></div>
        </div>
        <div class="btn-row">
          <button class="btn btn-take" id="take-btn">✓ Take Advice</button>
          <button class="btn btn-override" id="override-btn">✏️ Override</button>
        </div>
        <div class="override-input" id="override-box">
          <input type="text" id="override-input" placeholder="Your move (e.g. 13/8 6/3)">
          <button class="btn" style="width:100%;margin-top:4px;background:#555;" id="apply-override-btn">Apply Override</button>
        </div>
      </div>
    </div>

    <!-- Opponent turn -->
    <div class="card">
      <div class="card-title">Opponent's Turn</div>
      <div class="opp-inputs">
        <input class="opp-dice-input" id="opp-dice" type="text" placeholder="Dice (e.g. 4 2)">
        <input class="opp-move-input" id="opp-move" type="text" placeholder="Move (e.g. 24/18 13/9)">
      </div>
      <button class="btn next-btn" id="opp-apply-btn">Apply & Next Turn →</button>
    </div>

    <!-- Histogram -->
    <div class="card">
      <div class="card-title">All Dice Outcomes</div>
      <div id="histogram">
        <em style="color:#444">Get advice to see outcomes.</em>
      </div>
    </div>

  </div>
</main>
<script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 4: Commit**

```bash
git add templates/index.html static/style.css
git commit -m "feat: frontend HTML structure and CSS styling"
```

---

## Task 10: Frontend JavaScript

**Files:**
- Create: `static/app.js`

- [ ] **Step 1: Write app.js**

```javascript
// static/app.js
let currentPlan = 'wise';
let pendingAdvicedMove = null;

// ── Plan tabs ──
document.querySelectorAll('.plan-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.plan-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentPlan = tab.dataset.plan;
  });
});

// ── New game ──
document.getElementById('new-game-btn').addEventListener('click', async () => {
  const data = await post('/api/new-game', {});
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  clearHistory();
  document.getElementById('advice-result').style.display = 'none';
  document.getElementById('histogram').innerHTML = '<em style="color:#444">Get advice to see outcomes.</em>';
});

// ── Get advice ──
document.getElementById('advise-btn').addEventListener('click', async () => {
  const d1 = parseInt(document.getElementById('die1').value);
  const d2 = parseInt(document.getElementById('die2').value);
  if (!d1 || !d2 || d1 < 1 || d1 > 6 || d2 < 1 || d2 > 6) {
    alert('Enter two dice values (1–6).');
    return;
  }
  const data = await post('/api/advise', { dice: [d1, d2], plan: currentPlan });
  pendingAdvicedMove = data.best_move;
  document.getElementById('best-move-text').textContent = data.best_move || '—';
  document.getElementById('best-move-score').textContent = `Score: ${data.analysis.score}`;
  document.getElementById('advice-result').style.display = 'block';
  document.getElementById('override-box').classList.remove('visible');
  updateAnalysis(data.analysis);
  renderHistogram(data.histogram);
});

// ── Take advice ──
document.getElementById('take-btn').addEventListener('click', async () => {
  if (!pendingAdvicedMove || pendingAdvicedMove === '—') return;
  const data = await post('/api/apply-move', { move: pendingAdvicedMove });
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('you', pendingAdvicedMove);
  document.getElementById('advice-result').style.display = 'none';
  pendingAdvicedMove = null;
});

// ── Override ──
document.getElementById('override-btn').addEventListener('click', () => {
  document.getElementById('override-box').classList.toggle('visible');
});

document.getElementById('apply-override-btn').addEventListener('click', async () => {
  const move = document.getElementById('override-input').value.trim();
  if (!move) return;
  const data = await post('/api/apply-move', { move });
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('you', move);
  document.getElementById('advice-result').style.display = 'none';
  document.getElementById('override-input').value = '';
  pendingAdvicedMove = null;
});

// ── Opponent move ──
document.getElementById('opp-apply-btn').addEventListener('click', async () => {
  const diceStr = document.getElementById('opp-dice').value.trim();
  const move = document.getElementById('opp-move').value.trim();
  if (!move) return;
  const dice = diceStr.split(/\s+/).map(Number).filter(n => n >= 1 && n <= 6);
  const data = await post('/api/opponent-move', { dice, move });
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('opp', move, diceStr);
  document.getElementById('opp-dice').value = '';
  document.getElementById('opp-move').value = '';
});

// ── Helpers ──
async function post(url, body) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return resp.json();
}

function updateAnalysis(a) {
  document.getElementById('win-pct').textContent = a.win_pct + '%';
  document.getElementById('gammon-pct').textContent = a.gammon_pct + '%';
  document.getElementById('bg-pct').textContent = a.backgammon_pct + '%';
  const cubeBox = document.getElementById('cube-box');
  const cubeAction = document.getElementById('cube-action');
  const cubeOpp = document.getElementById('cube-opp');
  cubeBox.className = 'cube-box ' + a.cube.action;
  const labels = { double: '💡 Double now', hold: '✋ Hold cube', beware: '⚠️ Watch out' };
  cubeAction.textContent = labels[a.cube.action] || a.cube.action;
  cubeOpp.textContent = a.cube.opponent_should !== 'n/a'
    ? `Opp: ${a.cube.opponent_should}` : '';
}

function updateBoard(board) {
  renderPoints(board);
  document.getElementById('bar-red').textContent = board.red_bar;
  document.getElementById('bar-white').textContent = board.white_bar;
  // Pip counts are returned via analysis; approximate here from points
  let redPip = 0, whitePip = 0;
  for (let i = 1; i <= 24; i++) {
    if (board.points[i] > 0) redPip += board.points[i] * i;
    if (board.points[i] < 0) whitePip += (-board.points[i]) * (25 - i);
  }
  redPip += board.red_bar * 25;
  whitePip += board.white_bar * 25;
  document.getElementById('pip-red').textContent = redPip;
  document.getElementById('pip-white').textContent = whitePip;
}

function renderPoints(board) {
  const topRow = document.getElementById('top-row');
  const botRow = document.getElementById('bot-row');
  topRow.innerHTML = '';
  botRow.innerHTML = '';

  // Top row: points 13-18 (left of bar), 19-24 (right of bar)
  const topPoints = [13,14,15,16,17,18, null, 19,20,21,22,23,24];
  topPoints.forEach((pt, idx) => {
    if (pt === null) { topRow.appendChild(barSpacer()); return; }
    topRow.appendChild(makePoint(pt, board.points[pt], 'top', idx % 2 === 0 ? 'dark' : 'light'));
  });

  // Bottom row: points 12-7 (left of bar), 6-1 (right of bar)
  const botPoints = [12,11,10,9,8,7, null, 6,5,4,3,2,1];
  botPoints.forEach((pt, idx) => {
    if (pt === null) { botRow.appendChild(barSpacer()); return; }
    botRow.appendChild(makePoint(pt, board.points[pt], 'bot', idx % 2 === 0 ? 'light' : 'dark'));
  });
}

function makePoint(pt, count, rowType, triClass) {
  const div = document.createElement('div');
  div.className = 'point';
  const tri = document.createElement('div');
  tri.className = `point-triangle tri-${triClass}`;
  div.appendChild(tri);
  const color = count > 0 ? 'red' : 'white';
  const n = Math.abs(count);
  for (let i = 0; i < n; i++) {
    const c = document.createElement('div');
    c.className = `checker ${color}`;
    div.appendChild(c);
  }
  return div;
}

function barSpacer() {
  const s = document.createElement('div');
  s.style.width = '24px';
  s.style.flexShrink = '0';
  return s;
}

function renderHistogram(hist) {
  const el = document.getElementById('histogram');
  el.innerHTML = '';
  const maxAbs = Math.max(...hist.map(e => Math.abs(e.score)), 0.01);
  hist.forEach(entry => {
    const row = document.createElement('div');
    row.className = 'hist-entry';
    const label = entry.dice.join('-');
    const pct = Math.round((Math.abs(entry.score) / maxAbs) * 100);
    const barClass = entry.score > 0.05 ? 'bar-pos' : entry.score < -0.05 ? 'bar-neg' : 'bar-neu';
    const valColor = entry.score > 0.05 ? '#2ecc71' : entry.score < -0.05 ? '#e74c3c' : '#f39c12';
    row.innerHTML = `
      <span class="hist-dice">${label}</span>
      <div class="hist-bar-bg"><div class="hist-bar ${barClass}" style="width:${pct}%"></div></div>
      <span class="hist-val" style="color:${valColor}">${entry.score >= 0 ? '+' : ''}${entry.score.toFixed(2)}</span>
    `;
    row.title = `Best: ${entry.best_move}`;
    el.appendChild(row);
  });
}

function addHistoryEntry(player, move, dice) {
  const log = document.getElementById('history-log');
  if (log.querySelector('em')) log.innerHTML = '';
  const div = document.createElement('div');
  div.className = `history-entry ${player}`;
  div.textContent = player === 'you'
    ? `You: ${move}`
    : `Opp: ${dice ? dice + ' → ' : ''}${move}`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function clearHistory() {
  document.getElementById('history-log').innerHTML = '<em style="color:#444">Move history will appear here.</em>';
}

// Load state on page open
(async () => {
  const resp = await fetch('/api/state');
  if (resp.ok) {
    const data = await resp.json();
    updateBoard(data.board);
    updateAnalysis(data.analysis);
    data.history.forEach(h => addHistoryEntry(h.player, h.move, h.dice ? h.dice.join(' ') : ''));
  } else {
    // No active game — auto-start one
    const data = await post('/api/new-game', {});
    updateBoard(data.board);
    updateAnalysis(data.analysis);
  }
})();
```

- [ ] **Step 2: Manually test the app**

```bash
source venv/bin/activate && python app.py
```

Open http://localhost:5000. Verify:
- Board renders at opening position with red and white checkers
- Plan tabs switch active style
- Entering dice 6+1 and clicking "Get Advice" returns a move and histogram
- "Take Advice" updates the board
- "Override" shows input field
- Opponent move input updates board and adds to history
- "New Game" resets everything

- [ ] **Step 3: Commit**

```bash
git add static/app.js
git commit -m "feat: frontend JavaScript - board rendering, API calls, UI interactions"
```

---

## Task 11: GitHub Integration

**Files:** None (git remote setup)

- [ ] **Step 1: Create GitHub repo**

Go to https://github.com/new. Create a repo named `backgammon-advisor`. Leave it empty (no README). Copy the remote URL (e.g. `https://github.com/YOUR_USERNAME/backgammon-advisor.git`).

- [ ] **Step 2: Add remote and push**

```bash
git remote add origin https://github.com/YOUR_USERNAME/backgammon-advisor.git
git push -u origin main
```

- [ ] **Step 3: Verify**

Visit `https://github.com/YOUR_USERNAME/backgammon-advisor` — confirm all files are there, CLAUDE.md is visible on the repo page.

- [ ] **Step 4: Add .superpowers to .gitignore (if not already)**

```bash
echo ".superpowers/" >> .gitignore
git add .gitignore && git commit -m "chore: ignore .superpowers brainstorm files"
git push
```

---

## Running Locally (Quick Reference)

```bash
cd /home/meron/backgammon-advisor
source venv/bin/activate
python app.py        # http://localhost:5000
pytest               # run all tests
```
