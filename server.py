from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
import os
import subprocess

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app) # Enables GitHub Pages front-end to call this API without Cross-Origin blocking

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/maia')
def maia_page():
    return app.send_static_file('maia.html')

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
        raw_rating = int(rating_str)
        # Clamp to 1100-1900 range
        raw_rating = max(1100, min(1900, raw_rating))
        # Round to nearest 100 to map to an available model
        rating = round(raw_rating / 100.0) * 100
    except ValueError:
        return jsonify({"error": "Rating must be an integer"}), 400

    result = get_maia_move(fen, rating)
    
    # Let's also include the requested_rating so users know what was processed
    if "error" not in result:
        result["requested_rating"] = int(rating_str)

    if "error" in result:
        return jsonify(result), 500
        
    return jsonify(result)

if __name__ == "__main__":
    # Run the server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
