#!/usr/bin/env python3
import argparse
import requests
import json
import sys
import os

def fetch_puzzles(rating, theme, count, output_file=None):
    url = f"https://chughjug.github.io/tactics/api/puzzles/{rating}.json"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            err = {"error": f"Failed to fetch data for rating {rating}. It may not exist."}
            print(json.dumps(err))
            sys.exit(1)
            
        puzzles = response.json()
        
        # Filter by theme
        if theme:
            theme_lower = theme.lower().strip()
            puzzles = [p for p in puzzles if theme_lower in [t.lower() for t in p.get('themes', [])]]
            
        # Limit to the requested count
        puzzles = puzzles[:count]
        
        # Format the output to hold puzzle n, fen, and soln
        formatted = []
        for n, p in enumerate(puzzles, 1):
            formatted.append({
                "n": n,
                "id": p["id"],
                "fen": p["fen"],
                "soln": p["moves"]
            })
            
        if output_file:
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(formatted, f, indent=4)
        else:
            # Print to stdout so it can be piped/used by other scripts anywhere
            print(json.dumps(formatted, indent=4))
            
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Fetch and filter puzzles from the static GitHub Pages API.")
    # parser.add_argument("--rating", type=int, default=1500, help="The rating block to search (e.g., 1500)")
    # parser.add_argument("--theme", type=str, default="", help="Theme to filter by (e.g., fork, endgame)")
    # parser.add_argument("--count", type=int, default=100, help="Number of puzzles to return")
    # parser.add_argument("--out", type=str, default="", help="Optional file to save the JSON output. If omitted, prints to console.")
    # 
    # args = parser.parse_args()
    # 
    # fetch_puzzles(rating=args.rating, theme=args.theme, count=args.count, output_file=args.out)

    # Temporarily hardcoded call
    print("Generating hardcoded puzzles (Rating: 1600, Theme: fork, Count: 30)...")
    fetch_puzzles(rating=1600, theme="fork", count=30, output_file="api/custom/latest_request.json")
    print("Done! Saved to api/custom/latest_request.json")