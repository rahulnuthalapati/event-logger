import { showEventsView } from './events.js';
import { apiURL } from './main.js';

export function setupAuthUI() {
    const registerBtn = document.getElementById('register-btn');
    const appNameInput = document.getElementById('app-name-input');
    const registerResult = document.getElementById('register-result');
    const loginBtn = document.getElementById('login-btn');
    const authTokenInput = document.getElementById('auth-token-input');
    const loginResult = document.getElementById('login-result');

    registerBtn.onclick = async () => {
        const appName = appNameInput.value.trim();
        if (!appName) {
            registerResult.innerHTML = `<div class='notification is-danger is-light p-2'>Please enter an application name.</div>`;
            return;
        }
        registerResult.innerHTML = `<div class='notification is-info is-light p-2'>Registering...</div>`;
        try {
            const response = await fetch(`${apiURL}/api/app/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: appName })
            });
            const data = await response.json();
            if (response.ok) {
                registerResult.innerHTML = `
                    <div class='notification is-success is-light p-2'>
                        JWT: <code id='jwt-token'>${data.token}</code>
                        <button id='copy-jwt' class='button is-small is-link is-light ml-2'>Copy</button>
                    </div>
                `;
                document.getElementById('copy-jwt').onclick = () => {
                    navigator.clipboard.writeText(data.token);
                };
                authTokenInput.value = data.token;
            } else {
                registerResult.innerHTML = `<div class='notification is-danger is-light p-2'>${data.detail || 'Registration failed.'}</div>`;
            }
        } catch (err) {
            registerResult.innerHTML = `<div class='notification is-danger is-light p-2'>Error: ${err}</div>`;
        }
    };

    // Helper to show/hide views
    function showAuthView() {
        document.getElementById('auth-container').style.display = '';
        document.getElementById('events-view').style.display = 'none';
        document.getElementById('navbar-back').classList.add('is-hidden');
        document.getElementById('navbar-refresh').classList.add('is-hidden');
    }

    async function fetchEvents(token) {
        const resp = await fetch(`${apiURL}/api/events`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!resp.ok) throw new Error('Invalid token or failed to fetch events');
        return await resp.json();
    }

    loginBtn.onclick = async () => {
        const token = authTokenInput.value.trim();
        if (!token) {
            loginResult.innerHTML = `<div class='notification is-danger is-light p-2'>Please enter an auth token.</div>`;
            return;
        }
        loginResult.innerHTML = `<div class='notification is-info is-light p-2'>Loading events...</div>`;
        try {
            const events = await fetchEvents(token);
            // Try to get app name from registration or fallback
            let appName = document.getElementById('app-name-input').value.trim();
            if (!appName) appName = 'Your Application';
            showEventsView(appName, events);
            window.refreshEvents = async function() {
                const token = authTokenInput.value.trim();
                if (!token) return;
                let appName = appNameInput.value.trim();
                if (!appName) appName = 'Your Application';
                try {
                    const events = await fetchEvents(token);
                    showEventsView(appName, events);
                } catch (err) {
                    // Optionally show error somewhere
                }
            };
            // Show refresh button when events are visible
            document.getElementById('navbar-refresh').classList.remove('is-hidden');
        } catch (err) {
            loginResult.innerHTML = `<div class='notification is-danger is-light p-2'>Error: ${err.message}</div>`;
        }
    };
    // Back button logic
    document.getElementById('navbar-back').onclick = () => {
        showAuthView();
    };
    // On load, show auth view
    showAuthView();
} 