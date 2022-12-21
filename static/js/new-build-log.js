// Get All Spareparts
var spareparts;
var first_row;
const url = window.location.origin + "/build-log/get-spareparts/";
let http = new XMLHttpRequest();
http.open("GET", url, true);
http.onreadystatechange = function () {
    if (http.readyState == 4 && http.status == 200) {
        spareparts = JSON.parse(http.responseText);
        materialKind(spareparts);
        first_row = document.querySelector("table tbody tr").outerHTML;
        calculateMaterialCost();

        hideFirstRow();
    }
};
http.send();

// Count Rows
function hideFirstRow() {
    let rows = document.querySelectorAll("table tbody tr").length;
    if (rows > 2) {
        document.querySelector("table tbody tr:first-child").style.display = "none";
    }
}

// Material Kind Select Option
function materialKind(spareparts) {
    let kind = document.getElementById("material-kind");
    for (let k in spareparts) {
        kind.innerHTML += `<option value="${k}">${k}</option>`;
    }
}

// Material Kind Event Listener
function selectKind(element) {
    let row = element.closest("tr");
    let key = element.value;
    let material = row.querySelector("#material-select");
    if (key != "None") {
        material.innerHTML = "";
        let ids = Object.keys(spareparts[key]);
        for (let i = 0; i < ids.length; i++) {
            let id = ids[i];
            let item_name = spareparts[key][id].name;
            if (i == 0) {
                material.innerHTML += `<option value="${id}" selected>${item_name}</option>`;
                row.setAttribute("id", id);
                setStockAndCost(row, spareparts[key][id]);
                calculateMaterialCost();
            } else {
                material.innerHTML += `<option value="${id}">${item_name}</option>`;
            }
        }
    } else {
        material.innerHTML = "<option selected>Select</option>";
    }
}

// Material Select Event Listener
function selectSparepart(element) {
    let row = element.closest("tr");
    let id = element.value;
    let key = row.querySelector("#material-kind").value;
    row.setAttribute("id", id);

    setStockAndCost(row, spareparts[key][id]);
}

function setStockAndCost(parentTag, sparepart) {
    let qty = 1;
    // Set value for Stock Left Column
    parentTag.querySelector("#material-stock-left").value = sparepart.in_stock - qty;
    parentTag.querySelector("#material-stock-out").setAttribute("max", sparepart.in_stock);
    parentTag.querySelector("#material-stock-out").setAttribute("value", qty);

    // Set value for Cost Column
    let col5 = parentTag.querySelector("#material-perunit-price");
    setValue(col5, Math.round(sparepart.price_perunit));

    // Set value for Total Cost Column
    let col6 = parentTag.querySelector("td:last-child");
    setValue(col6, sparepart.price_perunit * qty);
}

function calculateTotalCost(element) {
    let row = element.closest("tr");
    let stock_out = element.value;
    let perunit_cost = row.querySelector("#material-perunit-price").getAttribute("value");
    setValue(row.querySelector("td:last-child"), stock_out * Math.round(perunit_cost));
    updateStockLeft(row, element);
    calculateMaterialCost();
}

function updateStockLeft(parentTag, target) {
    let stock_left = parentTag.querySelector("#material-stock-left");
    let max_stock = target.getAttribute("max");
    stock_left.value = max_stock - target.value;
}

function calculateMaterialCost() {
    let total_cost = 0;
    let all_rows = document.querySelectorAll("table tr td:last-child");
    for (let i = 0; i < all_rows.length - 1; i++) {
        let cost = all_rows[i].getAttribute("value");
        if (cost) {
            total_cost += parseInt(Math.round(cost));
        }
    }
    let material_col = document.querySelector("table tr:last-child td:last-child");
    setValue(material_col, total_cost);
}

function setValue(element, value) {
    element.innerText = "Rp " + value.toLocaleString("en");
    element.setAttribute("value", value);
}

// Add More Row
document.getElementById("add-more").addEventListener("click", () => {
    // Add new row at the bottom of the table
    let table = document.querySelector("table tbody");
    let last_row = table.querySelector("tr:last-child");
    table.insertAdjacentHTML("beforeEnd", first_row);
    table.appendChild(last_row);
});

function removeRow(element) {
    let table = element.closest("tbody");
    let row = element.closest("tr");
    table.removeChild(row);
}

// Submit Button and Form Validation
function checkThis(className) {
    let value = document.getElementById(className).value;
    if (value != "") {
        return true;
    } else {
        return false;
    }
}
const check = {
    dateInput: () => {
        return checkThis("build-date");
    },
    titleInput: () => {
        return checkThis("build-title");
    },
};
document.getElementById("submit-button").addEventListener("click", (event) => {
    if (check.dateInput() && check.titleInput()) {
        event.target.setAttribute("type", "submit");
    } else if (!check.dateInput()) {
        alert("Date can not be empty!");
    } else if (!check.titleInput()) {
        alert("Title can not be empty!");
    }
});
