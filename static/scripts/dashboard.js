const logoutButton = document.getElementById('logoutButton');
const serversList = document.getElementById('servers-list');
const activeServers = document.getElementById('active-servers');
const onlinePlayers = document.getElementById('online-players');
const addServerButton = document.getElementById('add-server-button');

const socket = io();

let servers = [];

logoutButton.addEventListener("click", (e) => {
    window.location.replace("/logout");
});

let onlineServers = 0;
let totalServers = 0;
let onlinePlayersCount = 0;
let maxPlayers = 0;

function addServer(name, description, online, onlinePlayers, maxPlayers, software, version, id) {
    const server = document.createElement("div");
    server.className = "server";

    server.innerHTML = `
        <div>
            <h3>${name}</h3>
            <p>${description}</p>
            <p>${version}</p>
            <p>${software}</p>
            <p>id: ${id}</p>
        </div>

        <div>
            <p class="${online ? "online" : "offline"}">
                ● ${online ? "Online" : "Offline"}
            </p>
            <p>${onlinePlayers} / ${maxPlayers} player${onlinePlayers !== 1 ? "s" : ""}</p>
        </div>
    `;

    server.onclick = () => {
        window.location.href = `/server/${id}`;
    };

    serversList.appendChild(server);
};

function updateServers() {
    serversList.innerHTML = "";
    servers.forEach(server => {
        addServer(
            server.name,
            server.description,
            server.online,
            server.onlinePlayers,
            server.maxPlayer,
            server.software,
            server.version,
            server.id
        );
    })

    totalServers = servers.length;

    for (let i = 0; i < totalServers; i++) {
        if (servers[i].online) {
            onlineServers++;
        }

        maxPlayers += servers[i].maxPlayer;
        onlinePlayersCount += servers[i].onlinePlayers;
    }

    activeServers.textContent = `${onlineServers} / ${totalServers}`;
    onlinePlayers.textContent = `${onlinePlayersCount} / ${maxPlayers}`;

    onlineServers = 0;
    totalServers = 0;
    onlinePlayersCount = 0;
    maxPlayers = 0;

}

async function fetchServers() {
    socket.emit("getServersInfos");
};

socket.on("connect", () => {
    console.log("connected via websocket");
});

socket.on("disconnect", () => {
    console.error("websocket disconnected");
});

socket.on("serversInfos", (newServers) => {
    servers = newServers;
    updateServers();
})

setInterval(() => {
    fetchServers();
}, 1000)

addServerButton.addEventListener("click", () => {
    window.location.replace('/server/add')
})