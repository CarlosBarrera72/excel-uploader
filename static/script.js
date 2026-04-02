console.log("script loaded");

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const statusText = document.getElementById("status");

const previewSection = document.getElementById("preview-section");
const previewTableContainer = document.getElementById("preview-table-container");

const columnsSection = document.getElementById("columns-section");
const columnsList = document.getElementById("columns-list");
const processBtn = document.getElementById("process-btn");

const tableSection = document.getElementById("table-section");
const tableContainer = document.getElementById("table-container");

let currentFilename = "";
let currentHeaderRowIndex = null;
let selectedColumns = [];

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
        console.log("upload result:", result);

        if (!response.ok) {
            statusText.textContent = result.error || "Upload failed.";
            return;
        }

        currentFilename = result.filename;
        currentHeaderRowIndex = null;
        selectedColumns = [];

        statusText.textContent = result.message;

        columnsSection.classList.add("hidden");
        tableSection.classList.add("hidden");

        renderPreviewTable(result.preview_rows);

    } catch (error) {
        console.error(error);
        statusText.textContent = "Something went wrong during upload.";
    }
});

function renderPreviewTable(rows) {
    previewSection.classList.remove("hidden");
    previewTableContainer.innerHTML = "";

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    const rowHeader = document.createElement("th");
    rowHeader.textContent = "Row";
    headerRow.appendChild(rowHeader);

    const maxColumns = rows.reduce((max, row) => Math.max(max, row.length), 0);

    for (let i = 0; i < maxColumns; i++) {
        const th = document.createElement("th");
        th.textContent = `Column ${i + 1}`;
        headerRow.appendChild(th);
    }

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    rows.forEach((row, rowIndex) => {
        const tr = document.createElement("tr");

        const rowButtonCell = document.createElement("td");
        const rowButton = document.createElement("button");
        rowButton.type = "button";
        rowButton.textContent = `Use Row ${rowIndex + 1}`;
        rowButton.classList.add("row-select-btn");

        rowButton.addEventListener("click", () => {
            setHeaderRow(rowIndex);
        });

        rowButtonCell.appendChild(rowButton);
        tr.appendChild(rowButtonCell);

        for (let i = 0; i < maxColumns; i++) {
            const td = document.createElement("td");
            td.textContent = row[i] ?? "";
            tr.appendChild(td);
        }

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    previewTableContainer.appendChild(table);
}

async function setHeaderRow(rowIndex) {
    if (!currentFilename) {
        statusText.textContent = "No uploaded file found.";
        return;
    }

    statusText.textContent = `Setting Row ${rowIndex + 1} as header...`;

    try {
        const response = await fetch("/set-header", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: currentFilename,
                header_row_index: rowIndex
            })
        });

        const result = await response.json();
        console.log("set-header result:", result);

        if (!response.ok) {
            statusText.textContent = result.error || "Failed to set header row.";
            return;
        }

        currentHeaderRowIndex = rowIndex;
        selectedColumns = [];

        statusText.textContent = result.message;
        renderColumns(result.columns);

    } catch (error) {
        console.error(error);
        statusText.textContent = "Something went wrong while setting the header row.";
    }
}

function renderColumns(columns) {
    columnsSection.classList.remove("hidden");
    columnsList.innerHTML = "";

    columns.forEach((column) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = column;
        button.classList.add("column-btn");

        button.addEventListener("click", () => {
            if (selectedColumns.includes(column)) {
                selectedColumns = selectedColumns.filter((col) => col !== column);
                button.classList.remove("selected");
            } else {
                selectedColumns.push(column);
                button.classList.add("selected");
            }

            console.log("selectedColumns:", selectedColumns);
        });

        columnsList.appendChild(button);
    });
}

processBtn.addEventListener("click", async () => {
    if (!currentFilename) {
        statusText.textContent = "No uploaded file found.";
        return;
    }

    if (currentHeaderRowIndex === null) {
        statusText.textContent = "Please choose a header row first.";
        return;
    }

    if (selectedColumns.length === 0) {
        statusText.textContent = "Please select at least one column.";
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
                header_row_index: currentHeaderRowIndex,
                selected_columns: selectedColumns
            })
        });

        const result = await response.json();
        console.log("process result:", result);

        if (!response.ok) {
            statusText.textContent = result.error || "Processing failed.";
            return;
        }

        statusText.textContent = result.message;
        renderProcessedTable(result.columns, result.rows);

    } catch (error) {
        console.error(error);
        statusText.textContent = "Something went wrong during processing.";
    }
});

function renderProcessedTable(columns, rows) {
    tableSection.classList.remove("hidden");
    tableContainer.innerHTML = "";

    if (!rows || rows.length === 0) {
        tableContainer.innerHTML = "<p>No rows returned.</p>";
        return;
    }

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