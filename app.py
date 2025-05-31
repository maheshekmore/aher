from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import re
import io

app = Flask(__name__)

# Marathi OCR config
def extract_text(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image, lang='mar')
    return text

# Basic Marathi aher parsing
def parse_aher_text(text):
    name_pattern = re.compile(r'(?:(?:नाम|श्री)[:\-\s]*)?([\u0900-\u097F ]{2,})')
    amount_pattern = re.compile(r'([\u0966-\u096F]{1,5})')
    village_pattern = re.compile(r'(?:गाव[:\-\s]*)([\u0900-\u097F ]{2,})')

    lines = text.strip().split('\n')
    data = []

    for line in lines:
        if not line.strip():
            continue

        name_match = name_pattern.search(line)
        amount_match = amount_pattern.search(line)
        village_match = village_pattern.search(line)

        entry = {
            'name': name_match.group(1).strip() if name_match else '',
            'amount': amount_match.group(1) if amount_match else '',
            'village': village_match.group(1).strip() if village_match else ''
        }

        data.append(entry)

    return data

@app.route('/extract', methods=['POST'])
def extract():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    text = extract_text(image_file.read())
    parsed_data = parse_aher_text(text)

    return jsonify({'data': parsed_data})

if __name__ == '__main__':
    app.run(debug=True)
