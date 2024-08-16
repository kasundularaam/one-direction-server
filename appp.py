from flask import Flask, request, jsonify
import os
from process_image import predict_arrow

app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/upload_image', methods=['POST'])
def upload_image():

    if 'file' not in request.files:
        img_data = request.data
    else:
        img_data = request.files['file'].read()

    filename = "image_to_process.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, 'wb') as f:
        f.write(img_data)

    direction = predict_arrow(filepath)

    print(f"DIRECTION: {direction}")

    return jsonify({'direction': direction})


@app.route('/')
def index():
    return "SERVER IS RUNNING"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
