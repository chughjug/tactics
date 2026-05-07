document.addEventListener('DOMContentLoaded', () => {
    const ratingSelect = document.getElementById('ratingBlock');
    const searchBtn = document.getElementById('searchBtn');
    const resultsDiv = document.getElementById('results');
    const themeFilter = document.getElementById('themeFilter');

    // Parse URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const urlRating = urlParams.get('rating');
    const urlTheme = urlParams.get('theme');
    const urlCount = urlParams.get('count');
    const displayCount = urlCount ? parseInt(urlCount, 10) : 100;

    if (urlTheme) {
        themeFilter.value = urlTheme;
    }

    // Load available rating blocks from meta.json
    fetch('api/puzzles/meta.json')
        .then(response => response.json())
        .then(data => {
            ratingSelect.innerHTML = ''; // clear loading
            const options = data.available_ratings;
            
            // Set default: from URL if valid, else 1500.
            let selectedRating = urlRating ? parseInt(urlRating, 10) : 1500;
            let defaultIndex = options.indexOf(selectedRating);
            if (defaultIndex === -1) defaultIndex = options.indexOf(1500);
            if (defaultIndex === -1) defaultIndex = 0;

            options.forEach((block, index) => {
                const opt = document.createElement('option');
                opt.value = block;
                opt.textContent = `${block} - ${block + 99}`;
                if (index === defaultIndex) opt.selected = true;
                ratingSelect.appendChild(opt);
            });

            // Perform automatic search if URL parameters were provided
            if (urlRating || urlTheme) {
                performSearch(false);
            }
        })
        .catch(err => {
            console.error('Failed to load metadata:', err);
            ratingSelect.innerHTML = '<option value="">Error loading</option>';
        });

    searchBtn.addEventListener('click', () => {
        performSearch(true); // Update URL on manual click
    });

    function performSearch(updateUrl = false) {
        const selectedBlock = ratingSelect.value;
        const themeToFind = themeFilter.value.trim().toLowerCase();

        if (!selectedBlock) return;

        if (updateUrl) {
            const newUrl = new URL(window.location);
            newUrl.searchParams.set('rating', selectedBlock);
            if (themeToFind) {
                newUrl.searchParams.set('theme', themeFilter.value.trim());
            } else {
                newUrl.searchParams.delete('theme');
            }
            window.history.pushState({}, '', newUrl);
        }

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
                    // Shuffle filtered array and take up to displayCount
                    for (let i = filtered.length - 1; i > 0; i--) {
                        const j = Math.floor(Math.random() * (i + 1));
                        [filtered[i], filtered[j]] = [filtered[j], filtered[i]];
                    }
                    const selectedPuzzles = filtered.slice(0, displayCount);
                    displayPuzzles(selectedPuzzles);
                }
            })
            .catch(err => {
                console.error(err);
                resultsDiv.innerHTML = '<p>Error loading puzzles.</p>';
            })
            .finally(() => {
                searchBtn.disabled = false;
                searchBtn.textContent = 'Find Puzzles';
            });
    }

    function displayPuzzles(puzzles) {
        resultsDiv.innerHTML = '';
        puzzles.forEach(puzzle => {
            const themeHtml = puzzle.themes.filter(t => t).map(t => `<span class="theme">${t}</span>`).join('');
            
            const puzzleCard = document.createElement('div');
            puzzleCard.className = 'puzzle-card';
            puzzleCard.setAttribute('data-id', puzzle.id);
            puzzleCard.setAttribute('data-rating', puzzle.rating);
            puzzleCard.setAttribute('data-themes', puzzle.themes.join(','));
            puzzleCard.setAttribute('data-moves', puzzle.moves);
            puzzleCard.innerHTML = `
                <div class="puzzle-header">
                    <h3>Puzzle ID: <a href="https://lichess.org/training/${puzzle.id}" target="_blank" class="puzzle-link">${puzzle.id}</a></h3>
                    <strong class="puzzle-rating">Rating: ${puzzle.rating}</strong>
                </div>
                <div class="fen" data-fen="${puzzle.fen}">FEN: ${puzzle.fen}</div>
                <div class="themes-container" style="margin: 15px 0;">
                    <strong>Themes:</strong> 
                    <div class="themes" style="margin-top: 5px;">${themeHtml}</div>
                </div>
                <button class="solution-btn" onclick="document.getElementById('sol-${puzzle.id}').style.display='block'; this.style.display='none'">Show Solution</button>
                <div id="sol-${puzzle.id}" class="solution" data-moves="${puzzle.moves}">
                    <strong>Moves:</strong> <span class="moves-text">${puzzle.moves}</span>
                </div>
            `;
            resultsDiv.appendChild(puzzleCard);
        });
    }
});