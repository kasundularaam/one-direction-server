from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Ensure the dataset/left directory exists
UPLOAD_FOLDER = 'dataset/left'
DATASET_SIZE = 1000
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

image_count = 0


@app.route('/upload_image', methods=['POST'])
def upload_image():
    global image_count

    if image_count >= DATASET_SIZE:
        return jsonify({'message': f"All {DATASET_SIZE} images received. No more images accepted."}), 400

    if 'file' not in request.files:
        img_data = request.data
    else:
        img_data = request.files['file'].read()

    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f'image_{timestamp}_{image_count+1}.jpg'
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Save the image
    with open(filepath, 'wb') as f:
        f.write(img_data)

    image_count += 1
    print(f"Saved image {image_count}/1000: {filename}")

    return jsonify({'message': f'Image {image_count}/{DATASET_SIZE} received and saved'})


@app.route('/')
def index():
    return f"ESP32-CAM Image Receiver Server. Images received: {image_count}/{DATASET_SIZE}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
