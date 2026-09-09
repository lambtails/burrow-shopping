/**
 * Task handling code
 * Sends updates to the server to tell it a task is done
 */
const updateTask = (id, done = false) => {
    const url = "/update";
    const options = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            row_id: id,
            done: done,
        }),
    };
    fetch(url, options)
        .then((response) => response.text())
        .catch((error) => console.error("Error:", error));
};

document.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
    checkbox.addEventListener("input", (e) => {
        const elem = e.target;
        const rowid = parseInt(elem.id.split("-")[1]);
        updateTask(rowid, (done = elem.checked));
    });
});