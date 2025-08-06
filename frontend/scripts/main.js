import { setupAuthUI } from './auth.js';

document.addEventListener('DOMContentLoaded', () => {
    setupAuthUI();
    const refreshBtn = document.getElementById('navbar-refresh');
    if (refreshBtn) {
        refreshBtn.onclick = () => {
            if (window.refreshEvents) window.refreshEvents();
        };
    }
});
