/**
 * Grocery handling code
 * Sends updates to the server to tell it a grocery is selected/not
 */
const updateGrocery = (id, done = false) => {
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
        updateGrocery(rowid, (done = elem.checked));
    });
});

/** 
 * Local filtering code
 * Handles searching for items or filtering to a specific store
 */
const store_selector = document.getElementById("store-selector");
store_selector.addEventListener("input", (ev) => {
    // I'm using CSS to filter which elements are visible here
    // since it's significantly more performant than updating the DOM with JS
    const filter = ev.target.value;
    document.querySelector(".grid").id = filter;
});

const search = document.getElementById("search");
search.addEventListener("input", (ev)=>{
    // I'm also using CSS for the search, since it technically supports substring matching
    const search_string = ev.target.value.toString().toLowerCase();
    document.getElementById("dynamic-css").innerHTML = (
        search_string === "" 
            ? ""
            : `.grid .item:not([data-search*="${search_string}"]) {display:none;}`
    );
});
