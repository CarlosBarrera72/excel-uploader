from flask import Flask, render_template, request, jsonify, send_file # type: ignore
from io import BytesIO
import pandas as pd # type: ignore
import os 

app = Flask(__name__)

data_store = {}
processed_data_store = {}
header_store = {}

UPLOAD_FOLDER= "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    df = pd.read_excel(file)

    data_store[file.filename] = df

    preview_rows = df.head(10).values.tolist()

    return jsonify({
        "message" : 'File upload successful',
        "filename" : file.filename,
        "preview_rows" : preview_rows
    })
   

@app.route("/set-header", methods=["POST"])
def set_header():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    filename = data.get("filename")
    header_row_index = data.get("header_row_index")

    if filename not in data_store:
        return jsonify({"error": "File not found"}), 404

    try:
        df = data_store[filename].copy()

        if header_row_index < 0 or header_row_index >= len(df):
            return jsonify({"error": "Header row index out of range"}), 400

        headers = df.iloc[header_row_index].tolist()
        headers = [str(h).strip() for h in headers]

        df = df.iloc[header_row_index + 1:].reset_index(drop=True)
        df.columns = headers

        header_store[filename] = df.copy()

        return jsonify({
            "message": "Header row set successfully",
            "filename": filename,
            "columns": df.columns.tolist(),
            "preview": df.head(5).to_dict(orient="records")
        })

    except Exception as e:
        print("SET HEADER ERROR:", e)
        return jsonify({"error": "Failed to set header row"}), 500

@app.route("/process", methods=["POST"])
def process_file():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    filename = data.get("filename")
    selected_columns = data.get("selected_columns")

    if filename is None:
        return jsonify({"error": "Missing filename"}), 400

    if not selected_columns:
        return jsonify({"error": "No columns selected"}), 400

    if filename not in header_store:
        return jsonify({"error": "Header row has not been set"}), 404

    try:
        df = header_store[filename].copy()

        print("PROCESS DF COLUMNS:", df.columns.tolist())
        print("SELECTED COLUMNS:", selected_columns)

        df = df[selected_columns]

        processed_data_store[filename] = df.copy()

        return jsonify({
            "message": "Selection processed",
            "columns": df.columns.tolist(),
            "rows": df.to_dict(orient="records")
        })

    except Exception as e:
        print("PROCESS ERROR:", e)
        return jsonify({"error": str(e)}), 500
    
@app.route("/download/<fileName>", methods=["GET"])
def download_file(fileName):
    if fileName not in processed_data_store:
        return jsonify({"error": "No processed file available to download"}), 404

    try:
        df = processed_data_store[fileName]

        excel_buffer = BytesIO()

        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Processed Data")

        excel_buffer.seek(0)

        name, ext = os.path.splitext(fileName)
        download_name = f"{name}_processed.xlsx"

        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return jsonify({"error": "Failed to generate download"}), 500

if __name__ == "__main__":
    app.run(debug=True)