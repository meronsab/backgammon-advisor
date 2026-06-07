from backgammon.board import Board, generate_moves, apply_move, format_move, opening_board
from backgammon.evaluator import evaluate
from backgammon.opening_book import OPENING_BOOK

ALL_DICE_COMBOS = []
for _d1 in range(1, 7):
    for _d2 in range(_d1, 7):
        _dice = [_d1, _d2, _d1, _d2] if _d1 == _d2 else [_d1, _d2]
        _prob = (1/36) if _d1 == _d2 else (2/36)
        ALL_DICE_COMBOS.append((_dice, _prob))

_OPENING_POINTS = opening_board().points

def _is_opening(board: Board) -> bool:
    return (board.points == _OPENING_POINTS and
            board.red_bar == 0 and board.white_bar == 0 and
            board.red_off == 0 and board.white_off == 0)

def _score_move(board: Board, move: list, plan: str) -> float:
    new_board = apply_move(board, move, 'red')
    expected = 0.0
    for opp_dice, prob in ALL_DICE_COMBOS:
        opp_moves = generate_moves(new_board, opp_dice, 'white')
        if not opp_moves or opp_moves == [[]]:
            expected += prob * evaluate(new_board, plan)
        else:
            worst = min(evaluate(apply_move(new_board, m, 'white'), plan) for m in opp_moves)
            expected += prob * worst
    return expected

def best_move(board: Board, dice: list, plan: str = 'wise') -> list:
    moves = generate_moves(board, dice, 'red')
    if not moves or moves == [[]]:
        return []

    # Opening book: instant response on move 1
    if _is_opening(board):
        key = (dice[0], dice[-1], plan)
        if key in OPENING_BOOK:
            return OPENING_BOOK[key]

    return max(moves, key=lambda m: _score_move(board, m, plan))

def dice_histogram(board: Board, plan: str = 'wise') -> list:
    results = []
    for dice, prob in ALL_DICE_COMBOS:
        move = best_move(board, dice, plan)
        if move:
            score = evaluate(apply_move(board, move, 'red'), plan)
            move_str = format_move(move, 'red')
        else:
            score = evaluate(board, plan)
            move_str = '—'
        results.append({
            'dice': [dice[0], dice[1]],
            'score': round(score, 3),
            'prob': round(prob, 4),
            'best_move': move_str,
        })
    return sorted(results, key=lambda x: x['score'], reverse=True)
