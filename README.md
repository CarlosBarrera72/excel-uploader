# Excel Uploader App

A Flask-based web application that allows users to upload Excel or CSV files, inspect available columns, and choose which columns to display in the order they want.

---

# 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/excel-uploader.git
cd excel-uploader
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py

```
# Excel Uploader App

A Flask-based web application that allows users to upload Excel or CSV files, inspect available columns, and choose which columns to display in the order they want.

This README is written for a developer picking up the project for the first time and needing to get the application running locally.

---

## What This App Does

The application currently supports the following workflow:

1. User uploads a spreadsheet file
2. Backend reads the file
3. App identifies available columns
4. User selects the columns they want
5. App returns the data in the selected order
6. Processed data is displayed in the browser

---

## Tech Stack

### Backend
- Python
- Flask
- pandas
- openpyxl

### Frontend
- HTML
- CSS
- JavaScript

---

## Project Structure

```text
excel-uploader/
├── .venv/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── uploads/
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    └── index.html
