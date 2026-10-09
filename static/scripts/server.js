const tabs = document.querySelectorAll(".tab");
const contents = document.querySelectorAll(".tab-content");
const delete_server_button = document.getElementById("delete-server-button");
const back_button = document.getElementById("back-button");
const startButton = document.getElementsByClassName("start")[0];
const stopButton = document.getElementsByClassName("stop")[0];
const server_id = window.location.pathname.split("/").pop();
const terminal = document.getElementById("console-output");

const socket = io();

let waitingForLogs = true;

tabs.forEach(tab => {

    tab.addEventListener("click", () => {

        const target = tab.dataset.tab;


        tabs.forEach(t => t.classList.remove("active"));
        contents.forEach(c => c.classList.remove("active"));

        tab.classList.add("active");
        document.getElementById(target)
            .classList.add("active");

    });

});

delete_server_button.addEventListener("click", async () => {

    if (prompt("sure? [y/n]") == "y") {

        try {
            const response = await fetch("/api/server/delete", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    server_id: window.location.pathname.split("/").pop()
                })
            });

            const data = await response.json();

            if (response.ok) {
                window.location.replace("/dashboard");
            } else {
                console.error(data);
                alert("failed to delete server");
            }

        } catch (err) {
            console.error(err);
            alert("failed to delete server");
        }
    }
});

back_button.addEventListener("click", () => {
    window.location.replace('/dashboard');
})

startButton.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/server/start", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                server_id: window.location.pathname.split("/").pop()
            })
        });

        const data = await response.json();

        if (!response.ok) {
            console.error(data);
            alert("failed start server");
        }

    } catch (err) {
        console.error(err);
        alert("failed start server");
    }
}
);

stopButton.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/server/stop", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                server_id: window.location.pathname.split("/").pop()
            })
        });

        const data = await response.json();

        if (!response.ok) {
            console.error(data);
            alert("failed stop server");
        }

    } catch (err) {
        console.error(err);
        alert("failed stop server");
    }
}
);

function getServerLog(id) {
    socket.emit("getServerLog", {
        server_id: id
    });
}

setInterval(() => {
    getServerLog(server_id);
}, 1000);

socket.on("connect", () => {
    console.log("connected via websocket");
});

socket.on("disconnect", () => {
    console.error("websocket disconnected");
});

socket.on("logs", (data) => {

    if (data.logs) {
        data.logs.forEach(log => {

            if (waitingForLogs) {
                waitingForLogs = false;
                terminal.innerHTML = "";
            }

            const line = document.createElement("p");
            line.textContent = log;

            terminal.appendChild(line);

            terminal.scrollTop = terminal.scrollHeight;
        });
    }

});