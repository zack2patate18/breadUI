const backButton = document.getElementById('back-button');

const form = document.querySelector('form');

async function loadVersions() {
    const select = document.getElementById("version");

    try {
        const response = await fetch("/api/get-versions");
        const data = await response.json();

        select.innerHTML = '<option value="">Select version</option>';

        for (const version of data.versions) {
            const option = document.createElement("option");
            option.value = version;
            option.textContent = version;
            select.appendChild(option);
        }
    } catch (err) {
        console.error(err);
        select.innerHTML =
            '<option value="">Unable to load versions</option>';
    }
}

async function loadSoftwares() {
    const select = document.getElementById("software");

    try {
        const response = await fetch("/api/get-softwares");
        const data = await response.json();

        select.innerHTML = '<option value="">Select software</option>';

        for (const software of data.softwares) {
            const option = document.createElement("option");
            option.value = software;
            option.textContent = software;
            select.appendChild(option);
        }
    } catch (err) {
        console.error(err);
        select.innerHTML =
            '<option value="">Unable to load software</option>';
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await Promise.all([loadVersions(), loadSoftwares()]);
});

backButton.addEventListener('click', () => {
    window.location.replace('/dashboard')
})

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
        name: form.name.value,
        description: form.description.value,
        version: form.version.value,
        software: form.software.value,
        max_players: parseInt(form.max_players.value),
        port: parseInt(form.port.value)
    };

    const response = await fetch("/api/server/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (response.ok) {
        window.location.href = "/dashboard";
    };
    window.location.replace('/dashboard');
});