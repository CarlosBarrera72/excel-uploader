const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const statusText = document.getElementById("status");
const columnsSection = document.getElementById("columns-section");
const columnsList = document.getElementById("columns-list");
const processBtn = document.getElementById("process-btn");
const tableSection = document.getElementById("table-section");
const tableContainer = document.getElementById("table-container");

let currentFilename = "";
let selectedColumns = [];

console.log("Script loaded")

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        statusText.textContent = "Please choose a file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    statusText.textContent = "Uploading...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            statusText.textContent = result.error || "Upload failed.";
            return;
        }

        currentFilename = result.filename;
        selectedColumns = [];

        statusText.textContent = result.message;
        renderColumns(result.columns);

    } catch (error) {
        statusText.textContent = "Something went wrong during upload.";
        console.error(error);
    }
});

function renderColumns(columns) {
    columnsSection.classList.remove("hidden");
    tableSection.classList.add("hidden");
    columnsList.innerHTML = "";

    columns.forEach((column) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = column;
        button.classList.add("column-btn");

        button.addEventListener("click", () => {
            if (!selectedColumns.includes(column)) {
                selectedColumns.push(column);
                button.classList.add("selected");
            }
        });

        columnsList.appendChild(button);
    });
}

processBtn.addEventListener("click", async () => {
    if (!currentFilename || selectedColumns.length === 0) {
        statusText.textContent = "Select at least one column.";
        return;
    }

    statusText.textContent = "Processing file...";

    try {
        const response = await fetch("/process", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: currentFilename,
                selected_columns: selectedColumns
            })
        });

        const result = await response.json();

        console.log("process result:", result);
        console.log("response ok:", response.ok);

        if (!response.ok) {
            statusText.textContent = result.error || "Processing failed.";
            return;
        }

        statusText.textContent = result.message;
        renderTable(result.columns, result.rows);

    } catch (error) {
        statusText.textContent = "Something went wrong during processing.";
        console.error(error);
    }
});

function renderTable(columns, rows) {
    tableSection.classList.remove("hidden");
    tableContainer.innerHTML = "";

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    columns.forEach((column) => {
        const th = document.createElement("th");
        th.textContent = column;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    rows.forEach((row) => {
        const tr = document.createElement("tr");

        columns.forEach((column) => {
            const td = document.createElement("td");
            td.textContent = row[column] ?? "";
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    tableContainer.appendChild(table);
}