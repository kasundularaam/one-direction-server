from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS

import os
from process_image import predict_arrow
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_image', methods=['POST'])
def upload_image():
    img_data = request.data

    filename = "image_to_process.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, 'wb') as f:
        f.write(img_data)

    direction = predict_arrow(filepath)
    print(f"DIRECTION: {direction}")

    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    socketio.emit('data', {
                  'direction': direction, 'image': encoded_string}, namespace='/web')

    socketio.emit('data', {'direction': direction}, namespace='/esp32')

    return 'OK', 200


@socketio.on('connect', namespace='/web')
def handle_web_connect():
    print('Web client connected')
    socketio.emit('connection_response', {
                  'data': 'Web Connected'}, namespace='/web')


@socketio.on('disconnect', namespace='/web')
def handle_web_disconnect():
    print('Web client disconnected')


@socketio.on('connect', namespace='/esp32')
def handle_esp32_connect():
    print('ESP32 client connected')
    socketio.emit('connection_response', {
                  'data': 'ESP32 Connected'}, namespace='/esp32')


@socketio.on('disconnect', namespace='/esp32')
def handle_esp32_disconnect():
    print('ESP32 client disconnected')


@socketio.on('connect', namespace='/controller')
def handle_controller_connect():
    print('Controller client connected')
    socketio.emit('connection_response', {
                  'message': 'Controller Connected'}, namespace='/controller')


@socketio.on('direction', namespace='/controller')
def handle_controller_direction(data):
    socketio.emit('data', {'direction': data}, namespace='/esp32')
    print(data)


@socketio.on('disconnect', namespace='/controller')
def handle_controller_disconnect():
    print('Controller client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
