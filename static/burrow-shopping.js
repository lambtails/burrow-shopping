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
    const search_string = ev.target.value.toString().toUpperCase();
    document.getElementById("dynamic-css").innerHTML = (
        search_string === "" 
            ? ""
            : `.grid .item:not([data-search*="${search_string}"]) {display:none;}`
    );
});


/**
 * Add new item button
 */
const addNewGrocery = (name) => {
    const url = "/new-item";
    const options = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name,
        }),
    };
    fetch(url, options)
        .then((response) => response.text())
        .catch((error) => console.error("Error:", error));
};

const new_item = document.getElementById("new-item");
new_item.addEventListener("click", (ev) => {
    // Get user to input a string (without having to use a whole UI library)
    let item_name = prompt("Enter new item name");
    if (item_name != null) {
        // Add new grocery to database
        addNewGrocery(item_name);

        // Refresh page
        setTimeout(()=>{window.location.reload()}, 100);
    }
});