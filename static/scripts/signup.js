const usernameField = document.getElementById('username');
const passwordField = document.getElementById('password');
const passwordConfirmationField = document.getElementById('passwordConfirmation');
const form = document.getElementById('signupForm');
const message = document.getElementById('message');

async function signup(username, password, passwordConfirmation) {
    const response = await fetch("/api/signup", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password,
            passwordConfirmation: passwordConfirmation
        })
    });

    const resp = await response.json();

    message.textContent = resp.message;
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    signup(usernameField.value, passwordField.value, passwordConfirmationField.value);
})