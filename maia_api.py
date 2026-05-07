#!/usr/bin/env python3
import argparse
import sys
import os
import json
import chess
import chess.engine

import subprocess

def get_maia_move(fen, rating):
    # Determine the model path based on the selected rating
    models_dir = os.path.join(os.path.dirname(__file__), "maia-chess-master 2", "maia_weights")
    model_path = os.path.join(models_dir, f"maia-{rating}.pb.gz")
    
    if not os.path.exists(model_path):
        return {"error": f"Model for rating {rating} not found at {model_path}."}
    
    try:
        board = chess.Board(fen)
    except ValueError as e:
        return {"error": f"Invalid FEN string: {e}"}

    # Initialize the lc0 engine
    # Make sure lc0 is installed and accessible in the system PATH
    try:
        engine = chess.engine.SimpleEngine.popen_uci("lc0", stderr=subprocess.DEVNULL)
    except Exception as e:
        return {"error": f"Failed to start lc0 engine. Is it installed and in PATH? Error: {getattr(e, 'message', str(e))}"}

    try:
        # Configure lc0 to use the Maia weights
        engine.configure({"WeightsFile": model_path})
        
        # Maia is designed to play the "first thought" (nodes=1)
        limit = chess.engine.Limit(nodes=1)
        
        # Get the recommended move
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recommend a human-like move using Maia Chess.")
    parser.add_argument("--fen", type=str, required=True, help="FEN string of the current board state")
    parser.add_argument("--rating", type=int, choices=[1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900], required=True, help="Target Elo rating (1100-1900)")
    
    args = parser.parse_args()
    
    result = get_maia_move(args.fen, args.rating)
    if "error" in result:
        print(json.dumps(result))
        sys.exit(1)
        
    print(json.dumps(result, indent=4))
