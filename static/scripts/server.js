const tabs = document.querySelectorAll(".tab");
const contents = document.querySelectorAll(".tab-content");
const delete_server_button = document.getElementById("delete-server-button");
const back_button = document.getElementById("back-button");
const startButton = document.getElementsByClassName("start")[0];
const stopButton = document.getElementsByClassName("stop")[0];

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

        console.log(data);

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