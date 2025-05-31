import requests

API_URL = 'https://aher.onrender.com/extract'
image_path = 'sample_aher_image.jpg'  # Replace with your actual test image

with open(image_path, 'rb') as img_file:
    files = {'image': img_file}
    response = requests.post(API_URL, files=files)

if response.status_code == 200:
    print("✅ Response Data:")
    for row in response.json()['data']:
        print(row)
else:
    print("❌ Error:", response.status_code, response.text)
