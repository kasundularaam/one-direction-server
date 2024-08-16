from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os
from process_image import predict_arrow
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

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

    # Encode the image to base64 for sending to the client
    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # Emit the direction and image via WebSocket
    socketio.emit('prediction_result', {
                  'direction': direction, 'image': encoded_string})

    return 'OK', 200


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
