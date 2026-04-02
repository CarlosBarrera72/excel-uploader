const form = document.getElementById("upload-form");
const status = document.getElementById("status");

form.addEventListener("submit", function () {
    status.textContent = "Uploading...";
});