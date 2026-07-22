const usernameField = document.getElementById('username');
const passwordField = document.getElementById('password');
const form = document.getElementById('loginForm');
const message = document.getElementById('message');

async function login(username, password) {
    const response = await fetch("/api/login", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    const resp = await response.json();

    if (response.ok) {
        localStorage.setItem("temp_token", resp.temp_token);
    }

    message.textContent = resp.message;
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    login(usernameField.value, password.value);
})