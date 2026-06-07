from backgammon.board import opening_board, generate_moves
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
    entry = dice_histogram(b, 'wise')[0]
    assert 'dice' in entry
    assert 'score' in entry
    assert 'prob' in entry
    assert 'best_move' in entry

def test_dice_histogram_sorted_descending():
    b = opening_board()
    scores = [e['score'] for e in dice_histogram(b, 'wise')]
    assert scores == sorted(scores, reverse=True)
