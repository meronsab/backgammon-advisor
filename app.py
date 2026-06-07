from flask import Flask, request, jsonify, session, render_template
from backgammon.board import (
    opening_board, board_to_dict, board_from_dict,
    parse_move, apply_move, generate_moves, format_move
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

    def _expand_dice(dice):
        return dice * 2 if len(dice) == 2 and dice[0] == dice[1] else dice

    @app.post('/api/advise')
    def advise():
        if 'board' not in session:
            return jsonify({'error': 'No active game'}), 400
        data = request.get_json()
        dice = _expand_dice(data['dice'])
        plan = data.get('plan', 'wise')
        b = board_from_dict(session['board'])
        move = best_move(b, dice, plan)
        hist = dice_histogram(b, plan)
        move_str = format_move(move, 'red') if move else '—'
        new_b = apply_move(b, move, 'red') if move else b
        return jsonify({'best_move': move_str, 'histogram': hist, 'analysis': _analysis(new_b)})

    @app.post('/api/legal-moves')
    def legal_moves_route():
        if 'board' not in session:
            return jsonify({'error': 'No active game'}), 400
        data = request.get_json()
        dice = _expand_dice(data['dice'])
        player = data.get('player', 'red')
        b = board_from_dict(session['board'])
        moves = generate_moves(b, dice, player)
        result = [
            {'submoves': m, 'notation': format_move(m, player)}
            for m in moves if m
        ]
        return jsonify({'moves': result})

    @app.post('/api/apply-move')
    def apply_move_route():
        if 'board' not in session:
            return jsonify({'error': 'No active game'}), 400
        data = request.get_json()
        b = board_from_dict(session['board'])
        new_b = apply_move(b, parse_move(data['move'], 'red'), 'red')
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
        new_b = apply_move(b, parse_move(data['move'], 'white'), 'white')
        session['board'] = board_to_dict(new_b)
        history = session.get('history', [])
        history.append({'player': 'opp', 'dice': data.get('dice', []), 'move': data['move']})
        session['history'] = history
        return jsonify({'board': board_to_dict(new_b), 'analysis': _analysis(new_b)})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
