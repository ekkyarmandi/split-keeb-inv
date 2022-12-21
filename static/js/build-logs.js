const sold_btn = document.getElementById("is-sold-btn");
const modal = document.querySelector(".modal");
var material_cost;

function soldButton(e) {
    let tr = e.closest("tr");
    let title = tr.querySelector("td:nth-child(2)").innerText;
    let url = window.location.href + `${tr.getAttribute("id")}/sold/`;
    modal.querySelector("h1").innerText = title;
    modal.querySelector("form").setAttribute("action", url);
    material_cost = tr.querySelector("td:nth-child(3)").getAttribute("value");
    calculateExpectedPrice();
}

function calculateExpectedPrice() {
    let service_fee = document.getElementById("service-fee").value;
    let markup = document.getElementById("markup").value;
    let expected = document.getElementById("expected-price");
    let expected_price = parseInt(service_fee) + parseInt(material_cost) * (1 + parseInt(markup) / 100);
    expected.setAttribute("value", expected_price);
    expected.innerText = "Rp " + expected_price.toLocaleString("en");

    round_price = Math.round(expected_price / 1000) * 1000;
    expected.closest("div").querySelector("span:last-child").innerText = "Rp" + round_price.toLocaleString("en");

    let sold_price = document.getElementById("sold-price").value;
    if (sold_price > round_price) {
        let delta = sold_price - round_price;
        let perc = (100 * delta) / round_price;
        let profit = document.getElementById("sold-profit");
        profit.innerText = `Rp ${delta.toLocaleString("en")} (${perc.toFixed(2)}%)`;
    }
}
