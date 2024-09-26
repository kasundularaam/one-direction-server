import base64
from process_image import predict_arrow
import os
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask, render_template, request
import eventlet
eventlet.monkey_patch()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

current_direction = "stop"


def emit_fa_directions():
    eventlet.sleep(2)
    socketio.emit('data', {'direction': "left"}, namespace='/esp32')
    eventlet.sleep(0.5)
    socketio.emit('data', {'direction': "forward"}, namespace='/esp32')
    eventlet.sleep(2)
    socketio.emit('data', {'direction': "left"}, namespace='/esp32')
    eventlet.sleep(0.5)
    socketio.emit('data', {'direction': "forward"}, namespace='/esp32')
    eventlet.sleep(2)
    socketio.emit('data', {'direction': "stop"}, namespace='/esp32')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_image', methods=['POST'])
def upload_image():
    global current_direction

    img_data = request.data

    filename = "image_to_process.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, 'wb') as f:
        f.write(img_data)

    direction = predict_arrow(filepath)

    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    if direction == "no_arrow":
        direction = "forward"

    socketio.emit('data', {
        'direction': direction, 'image': encoded_string}, namespace='/web')

    current_direction = direction

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
    eventlet.spawn(emit_fa_directions)


@socketio.on('disconnect', namespace='/esp32')
def handle_esp32_disconnect():
    print('ESP32 client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
