from flask import Flask, render_template, request, jsonify # type: ignore
import pandas as pd # type: ignore
import os 

app = Flask(__name__)

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
   
    filename = file.filename or ""
    if not filename:
        return jsonify({"error": "No file selected"}), 400
    
    filepath = os.path.join(str(UPLOAD_FOLDER), str(filename))
    file.save(filepath)

    lower_name = filename.lower()

    try:
        if lower_name.endswith(".xlsx"):
            df = pd.read_excel(filepath, header=None, engine="openpyxl")
        elif lower_name.endswith(".csv"):
            df = pd.read_csv(filepath, header=None)
        else:
            return jsonify({"error": "Unsupported file type. Use .xlsx or .csv"}), 400
        
        df = df.fillna("")
        preview_rows = df.head(10).values.tolist()
        

        return jsonify({
            "message": "Upload successful",
            "filename": filename,
            "preview_rows": preview_rows
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    print("RAW JSON:", data)

    if not data:
        return jsonify({"error": "No JSON data received"}), 400
    
    filename = data.get("filename")
    header_row_index = data.get("header_row_index")
    selected_columns = data.get("selected_columns")

    if filename is None or header_row_index is None or not selected_columns:
        return jsonify({"error": "Missing filename, header row index, or selected columns"}), 400
    
    filepath = os.path.join(str(UPLOAD_FOLDER), str(filename))

    if not os.path.exists(filepath):
        return jsonify({"Error": "File not found"}), 404
    
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
        header = [str(h).strip() for h in headers]

        df = df.iloc[header_row_index + 1:].reset_index(drop=True)
        df.columns = headers

        df = df[selected_columns]
        df = df.fillna("")

        return jsonify({
            "message": "Processing successful", 
            "columns": selected_columns,
            "rows": df.to_dict(orient="records")
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)