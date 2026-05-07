document.addEventListener('DOMContentLoaded', () => {
    const ratingSelect = document.getElementById('ratingBlock');
    const searchBtn = document.getElementById('searchBtn');
    const resultsDiv = document.getElementById('results');
    const themeFilter = document.getElementById('themeFilter');

    // Load available rating blocks from meta.json
    fetch('api/puzzles/meta.json')
        .then(response => response.json())
        .then(data => {
            ratingSelect.innerHTML = ''; // clear loading
            const options = data.available_ratings;
            
            // Set 1500 as default if available
            let defaultIndex = options.indexOf(1500);
            if (defaultIndex === -1) defaultIndex = 0;

            options.forEach((block, index) => {
                const opt = document.createElement('option');
                opt.value = block;
                opt.textContent = `${block} - ${block + 99}`;
                if (index === defaultIndex) opt.selected = true;
                ratingSelect.appendChild(opt);
            });
        })
        .catch(err => {
            console.error('Failed to load metadata:', err);
            ratingSelect.innerHTML = '<option value="">Error loading</option>';
        });

    searchBtn.addEventListener('click', () => {
        const selectedBlock = ratingSelect.value;
        const themeToFind = themeFilter.value.trim().toLowerCase();

        if (!selectedBlock) return;

        searchBtn.disabled = true;
        searchBtn.textContent = 'Searching...';

        fetch(`api/puzzles/${selectedBlock}.json`)
            .then(res => res.json())
            .then(puzzles => {
                let filtered = puzzles;
                if (themeToFind) {
                    filtered = puzzles.filter(p => 
                        p.themes.some(t => t.toLowerCase().includes(themeToFind))
                    );
                }

                if (filtered.length === 0) {
                    resultsDiv.innerHTML = '<p>No puzzles found matching those criteria.</p>';
                } else {
                    // Pick a random puzzle from the filtered list
                    const randomIndex = Math.floor(Math.random() * filtered.length);
                    const puzzle = filtered[randomIndex];
                    displayPuzzle(puzzle);
                }
            })
            .catch(err => {
                console.error(err);
                resultsDiv.innerHTML = '<p>Error loading puzzles.</p>';
            })
            .finally(() => {
                searchBtn.disabled = false;
                searchBtn.textContent = 'Find a Puzzle';
            });
    });

    function displayPuzzle(puzzle) {
        const themeHtml = puzzle.themes.filter(t => t).map(t => `<span class="theme">${t}</span>`).join('');
        
        resultsDiv.innerHTML = `
            <div class="puzzle-card">
                <div class="puzzle-header">
                    <h3>Puzzle ID: <a href="https://lichess.org/training/${puzzle.id}" target="_blank">${puzzle.id}</a></h3>
                    <strong>Rating: ${puzzle.rating}</strong>
                </div>
                <div class="fen">FEN: ${puzzle.fen}</div>
                <div style="margin: 15px 0;">
                    <strong>Themes:</strong> 
                    <div class="themes" style="margin-top: 5px;">${themeHtml}</div>
                </div>
                <button class="solution-btn" onclick="document.getElementById('sol-${puzzle.id}').style.display='block'; this.style.display='none'">Show Solution</button>
                <div id="sol-${puzzle.id}" class="solution">Moves: ${puzzle.moves}</div>
            </div>
        `;
    }
});