// Radio button listener
const radio_btns = document.getElementsByName("inlineRadioOptions");
radio_btns.forEach((btn) => {
    btn.addEventListener("click", () => {
        const shipping_cost_input = document.getElementById("shippingCost");
        if (btn.value == "not free") {
            shipping_cost_input.removeAttribute("disabled");
        } else {
            shipping_cost_input.value = 0;
            shipping_cost_input.setAttribute("disabled", "");
        }
    });
});

// Shipping origin select listener
const origin_select = document.getElementById("shippingOriginSelect");
origin_select.addEventListener("change", () => {
    const shipping_origin = document.getElementById("shippingOrigin");
    if (origin_select.value == "new") {
        shipping_origin.removeAttribute("hidden");
    } else {
        shipping_origin.setAttribute("hidden", "");
    }
});

// Arrived checkbox listener
const arrived_check = document.getElementById("arrivedCheck");
var arrived = false;
arrived_check.addEventListener("click", () => {
    const arrived_date = document.getElementById("arrivedWrapper");
    if (!arrived) {
        arrived_date.removeAttribute("hidden");
        arrived = true;
    } else {
        arrived_date.setAttribute("hidden", "");
        arrived = false;
    }
});

// Add more item button action
const addMoreBtn = document.getElementById("addMoreItem");
addMoreBtn.addEventListener("click", addMore);
function addMore() {
    const items = document.getElementById("nItem");
    const item_container = document.getElementById("itemContainer");
    const item1 = document.getElementById("item1");
    n = parseInt(items.value);
    n += 1;

    // create new card
    let new_card = document.createElement("div");
    new_card.setAttribute("class", "card mb-2");
    new_card.setAttribute("id", "item" + n);

    // assign item1 elements to new card
    new_card.innerHTML = item1.innerHTML;

    // unhide the remove button
    let removeButton = new_card.querySelector("#removeButton");
    removeButton.removeAttribute("hidden");

    // Replace all item tag
    new_card.innerHTML = new_card.innerHTML.replaceAll("item1", "item" + n);

    // Append child to the item container
    item_container.appendChild(new_card);
    items.setAttribute("value",n);
}

function removeItem(e) {
    const item_container = document.getElementById("itemContainer");
    let target_child = document.getElementById(e.getAttribute("target"));
    item_container.removeChild(target_child);

    index = 1;
    cards = item_container.querySelectorAll(".card");
    cards.forEach((e) => {
        reindexItem(e, index);
        index += 1;
    });

    const items = document.getElementById("nItem");
    items.value -= 1;
}

function reindexItem(card, i) {
    let card_id = card.getAttribute("id");
    let label = card.querySelector("label");
    let del_btn = card.querySelector("div.d-flex span");
    let all_input = card.querySelectorAll("input");

    label.innerText = "Item " + i;
    card.setAttribute("id", "item" + i);
    all_input.forEach((e) => {
        input_name = e.getAttribute("name");
        e.setAttribute("name", input_name.replace(card_id, "item" + i));
    });
    if (del_btn) {
        del_btn.setAttribute("target", "item" + i);
    }
}

// Previous spareparts selections
function sparepartSelect(element) {
    let parent_tag = element.getAttribute("parent");
    let item_name = document.querySelector(`#${parent_tag} #itemName`);
    if (element.value == "new item") {
        item_name.removeAttribute("hidden");
    } else {
        item_name.setAttribute("hidden", "");
    }

    // populate item name, kind, link, and price
    let key = element.value;
    if (spareparts.hasOwnProperty(key)) {
        item_name.value = spareparts[key]["name"];
        document.querySelector(`#${parent_tag} #itemKind`).value = spareparts[key]["kind"];
        document.querySelector(`#${parent_tag} #itemLink`).value = spareparts[key]["link"];
        document.querySelector(`#${parent_tag} #itemPrice`).value = spareparts[key]["price"];
    }
}

// Sparepart form reset
function clearForm(e) {
    let item_id = e.getAttribute("target");
    document.querySelector(`div#${item_id} #itemName`).value = "";
    document.querySelector(`div#${item_id} #itemKind`).value = "";
    document.querySelector(`div#${item_id} #itemLink`).value = "";
    document.querySelector(`div#${item_id} #itemPrice`).value = "0";
    document.querySelector(`div#${item_id} #itemUnit`).value = "0";
    document.querySelector(`div#${item_id} #itemQty`).value = "0";
}
