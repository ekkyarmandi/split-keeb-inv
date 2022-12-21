function editSparepartModal(element) {
    const row = element.closest("tr");
    const sid = row.getAttribute("id");
    const modal = document.querySelector(".modal");

    // Set title, name, and kind value
    let name = row.querySelector("td:nth-child(4)").innerText;
    let kind = row.querySelector("td:nth-child(3)").innerText;
    modal.querySelector("h1").innerText = "Edit Sparepart #" + sid;
    modal.querySelector("#sparepart-name").value = name;
    modal.querySelector("#sparepart-kind").value = kind;

    // Set Edit Sparepart POST url
    form = modal.querySelector("form");
    form.setAttribute("action", `/edit-sparepart/${sid}/`);
}
