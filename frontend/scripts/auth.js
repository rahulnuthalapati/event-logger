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
            registerResult.textContent = 'Please enter an application name.';
            return;
        }
        registerResult.textContent = 'Registering...';
        try {
            const response = await fetch('http://localhost:8001/api/app/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: appName })
            });
            const data = await response.json();
            if (response.ok) {
                registerResult.innerHTML = `JWT: <code id='jwt-token'>${data.token}</code> <button id='copy-jwt'>Copy</button>`;
                document.getElementById('copy-jwt').onclick = () => {
                    navigator.clipboard.writeText(data.token);
                };
                authTokenInput.value = data.token;
            } else {
                registerResult.textContent = data.detail || 'Registration failed.';
            }
        } catch (err) {
            registerResult.textContent = 'Error: ' + err;
        }
    };

    loginBtn.onclick = () => {
        const token = authTokenInput.value.trim();
        if (!token) {
            loginResult.textContent = 'Please enter an auth token.';
            return;
        }
        loginResult.textContent = 'Logged in! Auth token: ' + token;
    };
} 