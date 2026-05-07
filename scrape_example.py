import requests
import json

# How to scrape the STATIC API
# Since the GitHub Pages site fetches data via JavaScript, BeautifulSoup won't see the puzzles from the HTML.
# Instead, you can query exactly what the site queries: the raw JSON data! This is MUCH faster and easier.

def scrape_puzzles(rating_group, theme_filter=None, limit=100):
    # Construct the URI to target JSON file directly
    url = f"https://chughjug.github.io/tactics/api/puzzles/{rating_group}.json"
    
    print(f"Fetching data from {url}...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch data. Error: {response.status_code}")
        return []
        
    puzzles = response.json()
    print(f"Successfully loaded {len(puzzles)} standard {rating_group}-rated puzzles.")
    
    # Filter using basic Python logic
    if theme_filter:
        theme_filter = theme_filter.lower()
        puzzles = [p for p in puzzles if theme_filter in [t.lower() for t in p['themes']]]
        print(f"Filtered down to {len(puzzles)} puzzles matching theme '{theme_filter}'.")
        
    return puzzles[:limit]

if __name__ == "__main__":
    # Example usage: Get 10 puzzles from the 1500 rating block that contain an endgame theme.
    my_puzzles = scrape_puzzles(rating_group=1500, theme_filter="endgame", limit=10)
    
    for i, puzzle in enumerate(my_puzzles, 1):
        print(f"\n--- Puzzle {i} ---")
        print(f"ID     : {puzzle['id']}")
        print(f"Rating : {puzzle['rating']}")
        print(f"Themes : {', '.join(puzzle['themes'])}")
        print(f"FEN    : {puzzle['fen']}")
        print(f"Moves  : {puzzle['moves']}")
