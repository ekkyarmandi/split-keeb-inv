function renameModalTitle(element) {
    let card_id = element.getAttribute("data-card-target");
    let card = document.getElementById(card_id);
    let card_title = card.querySelector(".card-title").textContent;

    let modal_title = document.getElementById("arrival-title");
    modal_title.innerText = card_title;

    let form = document.querySelector("form[method=post]");
    form.setAttribute("action", "/update-arrival/" + card_id + "/");
}
