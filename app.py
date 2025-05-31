import os
from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image
import pytesseract
import io
import pandas as pd

app = Flask(__name__)

# HTML for basic frontend
UPLOAD_FORM_HTML = """
<!DOCTYPE html>
<html lang="mr">
<head>
    <meta charset="UTF-8">
    <title>अहेर OCR</title>
</head>
<body>
    <h2>अहेर फोटो अपलोड करा (Marathi Handwriting)</h2>
    <form action="/extract" method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required><br><br>
        <input type="submit" value="OCR सुरू करा">
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(UPLOAD_FORM_HTML)

@app.route("/extract", methods=["POST"])
def extract_text():
    if "image" not in request.files:
        return "Image file is missing", 400

    image = Image.open(request.files["image"])
    text = pytesseract.image_to_string(image, lang="mar")

    rows = []
    for line in text.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split()
        amount = ""
        name = ""
        village = ""
        for part in parts:
            if part.replace("₹", "").replace(",", "").isdigit():
                amount = part.replace("₹", "")
            elif not name:
                name = part
            else:
                village += part + " "
        rows.append({"रक्कम": amount, "नाव": name, "गाव": village.strip()})

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(output, download_name="aher_output.xlsx", as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
