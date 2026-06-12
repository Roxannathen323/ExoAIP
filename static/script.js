document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('planet-search');
    const autocompleteList = document.getElementById('autocomplete-list');
    const searchForm = document.getElementById('search-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    let debounceTimer;

    // Autocomplete logika
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        
        clearTimeout(debounceTimer);
        if (query.length < 2) {
            autocompleteList.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    autocompleteList.innerHTML = '';
                    data.forEach(planet => {
                        const item = document.createElement('div');
                        item.className = 'autocomplete-item';
                        item.textContent = planet;
                        item.addEventListener('click', () => {
                            searchInput.value = planet;
                            autocompleteList.innerHTML = '';
                            submitSearch(planet);
                        });
                        autocompleteList.appendChild(item);
                    });
                });
        }, 300);
    });

    // Zavření našeptávače při kliknutí mimo
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !autocompleteList.contains(e.target)) {
            autocompleteList.innerHTML = '';
        }
    });

    // Odeslání formuláře
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const planet = searchInput.value;
        if (planet) {
            submitSearch(planet);
        }
    });

    function submitSearch(planetName) {
        const loader = document.querySelector('.terminal-loader');
        if (loader) loader.textContent = `ESTABLISHING DOWNLINK TO ${planetName.toUpperCase()}...`;
        loadingOverlay.style.display = 'flex';
        window.location.href = `/generate?planet=${encodeURIComponent(planetName)}`;
    }
});
