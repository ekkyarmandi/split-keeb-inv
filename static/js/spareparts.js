// get spareparts
var spareparts = {};
var xmlhttp = new XMLHttpRequest();
var endpoint = document.location.origin + "/spareparts/get";

// make a request to the end point
xmlhttp.open("GET", endpoint, true);
xmlhttp.send();

// get the response
xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {

        // parse the data
        spareparts = JSON.parse(this.responseText);

        // populate the sparepart select option
        let sparepartOptions = document.getElementById("sparepartOptions");
        for (const key in spareparts) {
            sparepartOptions.innerHTML += `<option value="${key}">${spareparts[key]["name"]}</option>`;
        }
    }
};