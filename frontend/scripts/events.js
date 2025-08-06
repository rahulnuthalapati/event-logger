// Event rendering and expand/collapse logic
export function showEventsView(appName, events) {
    document.getElementById('navbar-back').classList.remove('is-hidden');
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('events-view').style.display = '';
    document.getElementById('events-app-name').textContent = appName;
    const eventsList = document.getElementById('events-list');
    if (events.length === 0) {
        eventsList.innerHTML = '<p>No events found.</p>';
    } else {
        eventsList.innerHTML = events.map((ev, idx) => {
            // Display id, timestamp, and type in the summary if present
            const id = ev.id !== undefined ? ev.id : '-';
            const timestamp = ev.timestamp !== undefined ? ev.timestamp : '-';
            const type = ev.type !== undefined ? ev.type : '-';
            return `
                <div class='card mb-3 event-item' data-idx='${idx}'>
                    <header class='card-header event-summary is-clickable'>
                        <span class='card-header-title'>
                            <b>ID:</b> ${id} &nbsp; <b>Timestamp:</b> ${timestamp} &nbsp; <b>Type:</b> ${type}
                        </span>
                        <button class='button is-small is-link is-light event-toggle' aria-label='Expand/collapse event' style='margin-left: 1rem;'>&#x25BC;</button>
                    </header>
                    <div class='card-content event-details' style='display: none; background: #f5f5f5;'>
                        <pre>${JSON.stringify(ev, null, 2)}</pre>
                    </div>
                </div>
            `;
        }).join('');
        // Add expand/collapse logic
        Array.from(eventsList.getElementsByClassName('event-summary')).forEach((summary, idx) => {
            summary.onclick = function(e) {
                // Only prevent toggle if the button itself was clicked (let button work too)
                if (e.target.classList.contains('event-toggle')) {
                    // Let button click fall through to toggle as well
                }
                const item = summary.parentElement;
                item.classList.toggle('expanded');
                // Change arrow direction
                const btn = item.querySelector('.event-toggle');
                btn.innerHTML = item.classList.contains('expanded') ? '&#x25B2;' : '&#x25BC;';
            };
        });
    }
}
window.showEventsView = showEventsView; 