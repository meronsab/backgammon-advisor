from dataclasses import dataclass

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

def is_blocked(board: Board, point: int, player: str) -> bool:
    if player == 'red':
        return board.points[point] <= -2
    else:
        return board.points[point] >= 2

def apply_move(board: Board, move: list, player: str) -> Board:
    b = board.copy()
    for from_pt, to_pt in move:
        if player == 'red':
            if from_pt == 0:
                b.red_bar -= 1
            else:
                b.points[from_pt] -= 1
            if to_pt == 0:
                b.red_off += 1
            else:
                if b.points[to_pt] == -1:
                    b.points[to_pt] = 0
                    b.white_bar += 1
                b.points[to_pt] += 1
        else:
            if from_pt == 25:
                b.white_bar -= 1
            else:
                b.points[from_pt] += 1
            if to_pt == 25:
                b.white_off += 1
            else:
                if b.points[to_pt] == 1:
                    b.points[to_pt] = 0
                    b.red_bar += 1
                b.points[to_pt] -= 1
    return b

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
    if player == 'red':
        if from_pt == 0:
            to_pt = 25 - die
            if 19 <= to_pt <= 24 and not is_blocked(board, to_pt, 'red'):
                return to_pt
            return None
        to_pt = from_pt - die
        if to_pt >= 1:
            return to_pt if not is_blocked(board, to_pt, 'red') else None
        if all_home(board, 'red'):
            if to_pt == 0:
                return 0
            if to_pt < 0:
                highest = max((i for i in range(from_pt + 1, 7) if board.points[i] > 0), default=None)
                if highest is None:
                    return 0
        return None
    else:
        if from_pt == 25:
            to_pt = die
            if 1 <= to_pt <= 6 and not is_blocked(board, to_pt, 'white'):
                return to_pt
            return None
        to_pt = from_pt + die
        if to_pt <= 24:
            return to_pt if not is_blocked(board, to_pt, 'white') else None
        if all_home(board, 'white'):
            if to_pt == 25:
                return 25
            lowest = min((i for i in range(19, from_pt) if board.points[i] < 0), default=None)
            if lowest is None:
                return 25
        return None

def _checker_positions(board: Board, player: str) -> list:
    if player == 'red':
        return ([0] * board.red_bar +
                [i for i in range(1, 25) for _ in range(board.points[i]) if board.points[i] > 0])
    else:
        return ([25] * board.white_bar +
                [i for i in range(1, 25) for _ in range(-board.points[i]) if board.points[i] < 0])

def _gen_recursive(board: Board, dice: list, player: str, move_so_far: list, results: set):
    if not dice:
        results.add(tuple(move_so_far))
        return
    tried = set()
    all_checkers = set(_checker_positions(board, player))
    # Must enter from bar before moving any other piece
    bar = 0 if player == 'red' else 25
    on_bar = (player == 'red' and board.red_bar > 0) or (player == 'white' and board.white_bar > 0)
    checkers = {bar} if on_bar else all_checkers
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
    raw = set()
    _gen_recursive(board, dice[:], player, [], raw)
    if not raw:
        return [[]]
    max_len = max(len(m) for m in raw)
    best = [list(m) for m in raw if len(m) == max_len]
    if max_len == 1 and len(dice) == 2:
        max_die_used = max(abs(m[0][0] - m[0][1]) for m in best if m)
        best = [m for m in best if m and abs(m[0][0] - m[0][1]) == max_die_used]
    seen = set()
    deduped = []
    for m in best:
        key = frozenset(m)
        if key not in seen:
            seen.add(key)
            deduped.append(m)
    return deduped
