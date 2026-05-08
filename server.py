from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
import os
import subprocess

app = Flask(__name__)
CORS(app) # Enables GitHub Pages front-end to call this API without Cross-Origin blocking

def get_maia_move(fen, rating):
    models_dir = os.path.join(os.path.dirname(__file__), "maia-chess-master 2", "maia_weights")
    model_path = os.path.join(models_dir, f"maia-{rating}.pb.gz")
    
    if not os.path.exists(model_path):
        return {"error": f"Model for rating {rating} not found. Available ratings are 1100-1900."}
    
    try:
        board = chess.Board(fen)
    except ValueError as e:
        return {"error": f"Invalid FEN string: {e}"}

    try:
        # We suppress stderr so lc0 logs don't clutter the server output
        engine = chess.engine.SimpleEngine.popen_uci("lc0", stderr=subprocess.DEVNULL)
    except Exception as e:
        return {"error": f"Failed to start lc0 engine. Is it installed and in PATH? Error: {getattr(e, 'message', str(e))}"}

    try:
        engine.configure({"WeightsFile": model_path})
        limit = chess.engine.Limit(nodes=1)
        result = engine.play(board, limit)
        recommended_move = result.move.uci() if result.move else None
        
        return {
            "fen": fen,
            "rating": rating,
            "recommended_move": recommended_move
        }
    except Exception as e:
        return {"error": f"Error during engine evaluation: {str(e)}"}
    finally:
        engine.quit()

@app.route('/api/maia', methods=['GET'])
def maia_endpoint():
    fen = request.args.get('fen', default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    rating_str = request.args.get('rating', default="1100")
    
    try:
        rating = int(rating_str)
    except ValueError:
        return jsonify({"error": "Rating must be an integer"}), 400
        
    if rating not in [1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]:
        return jsonify({"error": "Invalid rating. Must be between 1100 and 1900 in increments of 100."}), 400

    result = get_maia_move(fen, rating)
    
    if "error" in result:
        return jsonify(result), 500
        
    return jsonify(result)

if __name__ == "__main__":
    # Run the server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
