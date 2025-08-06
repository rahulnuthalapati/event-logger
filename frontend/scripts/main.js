import { setupAuthUI } from './auth.js';

export const apiURL = 'http://localhost:8001';

document.addEventListener('DOMContentLoaded', () => {
    setupAuthUI();
    const refreshBtn = document.getElementById('navbar-refresh');
    if (refreshBtn) {
        refreshBtn.onclick = () => {
            if (window.refreshEvents) window.refreshEvents();
        };
    }
});
