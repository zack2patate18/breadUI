const logoutButton = document.getElementById('logoutButton');

function logout() {
    window.location.replace(`/logout?temp_token=${localStorage.getItem("token")}&username=${localStorage.getItem("username")}`);
}

logoutButton.addEventListener("click", (e) => {
    logout();
    
})