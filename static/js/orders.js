function duplicateFirstItem() {
    let item_container = document.querySelector(".item-container");
    let cloned = document.querySelector(".item-container > div").cloneNode(true);
    cloned.insertAdjacentHTML("afterBegin", '<hr class="my-0"/>');
    item_container.insertAdjacentElement("beforeEnd", cloned);
    itemListener();
    priceInputListener();
    kindDropdownListener();

    // Show the close row instruction
    document.querySelector(".close-row-info").style.display = "block";
}

// Item listener
function itemListener() {
    let item_container = document.querySelectorAll(".item-container > div");
    item_container.forEach((item, i) => {
        if (i > 0) {
            item.addEventListener("click", (element) => {
                let parent = element.target.closest(".order-items");
                if (element.ctrlKey) {
                    parent.outerHTML = "";

                    // Hide the close row instruction
                    if (item_container.length <= 2) {
                        document.querySelector(".close-row-info").style.display = "none";
                    }
                }
            });
        }
    });
}

// Peritem Price
function priceInputListener(element) {
    if (element) {
        // Get item values
        let parent = element.closest(".price-wrapper");
        let is_usd = document.getElementById("is-usd");
        let shipping_fee = parseFloat(document.getElementById("shipping-cost").value); // currency
        let idr = parseFloat(document.getElementById("usd-to-idr").value); // fixed currency
        let tax = parseInt(document.getElementById("tax").value); // fixed currency
        let price = parseFloat(parent.querySelector("#item-price").value); // currency
        let qty = parseInt(parent.querySelector("#item-qty").value);
        let unit = parseInt(parent.querySelector("#item-unit").value);

        // Calculate price perunit
        let sum_product_price = totalProductPrice();
        let p = (price * qty) / sum_product_price;
        let total = 0;
        if (is_usd.checked) {
            total = tax + idr * (shipping_fee + sum_product_price);
        } else {
            total = shipping_fee + tax + sum_product_price;
        }
        let price_perunit = p * total;
        if (qty > 0) {
            price_perunit = Math.round(price_perunit / (qty * unit));
        } else {
            price_perunit = 0;
        }
        parent.querySelector("#price-perunit").value = price_perunit;
    }
}

function totalProductPrice() {
    let price = document.getElementsByName("item-price"); // currency
    let qty = document.getElementsByName("item-qty");
    let total = 0;
    for (let i = 0; i < price.length; i++) {
        total += price[i].value * qty[i].value;
    }
    return total;
}

// Kind dropdown event listener
function kindDropdownListener() {
    document.querySelectorAll("ul.dropdown-menu").forEach((item) => {
        item.addEventListener("click", (event) => {
            let parent = item.closest(".order-items");
            parent.querySelector("#item-kind").value = event.target.textContent;
        });
    });
}
kindDropdownListener();

// Currency Settings
const currency = document.getElementById("currency");
currency.addEventListener("click", (e) => {
    let w = e.target.closest(".col");
    if (e.target.innerText == "Rp") {
        e.target.innerText = "$";
        w.querySelector("input[type=checkbox]").setAttribute("checked", "");
        changeCurrency("$");
    } else {
        e.target.innerText = "Rp";
        w.querySelector("input[type=checkbox]").removeAttribute("checked");
        changeCurrency("Rp");
    }
});

// Look for another the same currency span exclude Tax
function changeCurrency(symbol) {
    document.querySelectorAll("span.currency").forEach((span) => {
        span.innerText = symbol;
    });
}
