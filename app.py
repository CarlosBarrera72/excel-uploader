from flask import Flask, render_template, request, jsonify, send_file # type: ignore
from io import BytesIO
import pandas as pd # type: ignore
import os 

app = Flask(__name__)

data_store = {}

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

    return jsonify({
        "success" : 'file upload successful',
        "filename" : file.filename,
        "columns" : df.columns.tolist()
    })
   

@app.route("/set-header", methods=["POST"])
def set_header():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    filename = data.get("filename")
    header_row_index = data.get("header_row_index")

    if filename is None or header_row_index is None:
        return jsonify({"error": "Missing filename or header row index"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    lower_name = filename.lower()

    try:
        if lower_name.endswith(".xlsx"):
            df = pd.read_excel(filepath, header=None, engine="openpyxl")
        elif lower_name.endswith(".csv"):
            df = pd.read_csv(filepath, header=None)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        df = df.fillna("")

        headers = df.iloc[header_row_index].tolist()
        headers = [str(h).strip() for h in headers]

        df = df.iloc[header_row_index + 1:].reset_index(drop=True)
        df.columns = headers

        return jsonify({
            "message": "Header row set successfully",
            "filename": filename,
            "columns": headers
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/process", methods=["POST"])
def process_file():
    data = request.get_json()

    filename = data.get("filename")
    header_row_index = data.get("header_row_index")
    selected_columns = data.get("selected_columns")    

    if not data:
        return jsonify({"error": "No JSON data received"}), 400
    
    if not selected_columns:
        return jsonify({"error": "No column selected"}), 400

    if filename not in data_store:
        return jsonify({"error": "File not found"}), 404
    
    if header_row_index is None:
        return jsonify({"error":"Header row index missing"}), 400
    
    if header_row_index >= len(df) or header_row_index < 0 :
        return jsonify({"error": "Header row index out of range"}), 400

    try:
        df = data_store[filename].copy()
        headers = df.iloc[header_row_index].tolist()
        header = [str(h).strip() for h in headers]

        df = df.iloc[header_row_index + 1:]

        df = df.reset_index(drop=True)

        df.columns = header

        df = df[selected_columns]

        return jsonify({
            "message": "Selection processed",
            "columns": selected_columns,
            "rows" : df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": "No file to process"}), 500
    
@app.route("/download/<fileName>", methods=["GET"])
def download_file(fileName):
    
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], fileName)

    if not os.path.exists(file_path):
        return jsonify({"error": "No File Name"}), 404

    try:

        allowed_extensions = (".xlsx", ".xls")

        name, ext = os.path.splitext(fileName)
        ext = ext.lower()

        if ext not in allowed_extensions:
            return jsonify({"error":"File Type not supported"}), 400
        
        df = pd.read_excel(file_path)

        csv_filename = name + ".csv"

        csv_buffer = BytesIO()
        csv_string = df.to_csv(index=False)
        csv_buffer.write(csv_string.encode())
        
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to process file"}), 500
    
    csv_buffer.seek(0)

    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name=csv_filename,
        mimetype="text/csv"
    )



if __name__ == "__main__":
    app.run(debug=True)