from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from datetime import datetime


import os
from process_image import predict_arrow
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'dataset/no_arrow'
DATASET_SIZE = 1000
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


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

    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    socketio.emit('data', {
                  'direction': f"{image_count}", 'image': encoded_string}, namespace='/web')

    return jsonify({'message': f'Image {image_count}/{DATASET_SIZE} received and saved'})


@socketio.on('connect', namespace='/web')
def handle_web_connect():
    print('Web client connected')
    socketio.emit('connection_response', {
                  'data': 'Web Connected'}, namespace='/web')


@socketio.on('disconnect', namespace='/web')
def handle_web_disconnect():
    print('Web client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
