import os
from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image
import pytesseract
import pandas as pd
import io

app = Flask(__name__)

# Optional: Local development config
# os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata'
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update this path as per your system

# @app.route('/')
# def home():
#     return 'Aher OCR API is running. Use /extract to POST image.'

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

@app.route('/extract', methods=['POST'])
def extract_text():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']

    try:
        # Load and convert the image
        image = Image.open(file.stream).convert("RGB")
    except Exception:
        return jsonify({'error': 'Unsupported image format/type'}), 400

    # Extract text using pytesseract with Marathi language
    try:
        text = pytesseract.image_to_string(image, lang='mar')
    except Exception as e:
        return jsonify({'error': f'OCR failed: {str(e)}'}), 500

    # Parse the extracted text
    rows = []
    for line in text.split('\n'):
        parts = [p.strip() for p in line.split('–') if p.strip()]
        if len(parts) >= 2:
            name = parts[0]
            amount = parts[1].replace('₹', '').strip() if '₹' in parts[1] else ''
            village = parts[2] if len(parts) > 2 else ''
            rows.append({'नाव': name, 'रक्कम': amount, 'गाव': village})

    if not rows:
        return jsonify({'error': 'No valid entries detected'}), 200

    # Convert to Excel
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return (
        output.read(),
        200,
        {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename=aher_output.xlsx'
        }
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=10000, debug=True)
