from flask import Flask, render_template, request # type: ignore
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
    if "file" not in request.files:
        return "No file uploaded"
    
    file = request.file["file"]

    if file.filename == "":
        return "No file selected"
    
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    return f"Uploaded: {file.filename}"

if __name__ == "__main__":
    app.run(debug=True)