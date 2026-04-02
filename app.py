from flask import Flask, render_template, request, jsonify
import pandas as pd
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
        return jsonify({"No file selected"}), 400
   
    filename = file.filename or ""
    filepath = os.path.join(str(UPLOAD_FOLDER), str(filename))
    file.save(filepath)

    lower_name = filename.lower()

    try:
        if lower_name.endswith(".xlsx"):
            df = pd.read_excel(filepath, engine="openpyxl")
        elif lower_name.endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            return jsonify({"error": "Unsupported file type. Use .xlsx or .csv"}), 400

        coulmns = df.columns.tolist()

        return jsonify({
            "message": "Upload successful",
            "filename": filename,
            "columns": coulmns
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/process", methods=["POST"])
def process_file():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data recieved"}), 400
    
    filename = data.get("filename")
    selected_columns = data.get("selected_coulmns")

    if not filename or not selected_columns:
        return jsonify({"error": "Missing filename or selected columns"}), 400
    
    filepath = os.path.join(str(UPLOAD_FOLDER), str(filename))

    if not os.path.exists(filepath):
        return jsonify({"Error": "File not found"}), 400

if __name__ == "__main__":
    app.run(debug=True)