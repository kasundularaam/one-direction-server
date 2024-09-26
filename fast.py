from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
import os
import base64
from process_image import predict_arrow
import tensorflow as tf

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

current_direction = "stop"

# Load the TensorFlow model at startup
model = tf.keras.models.load_model('one_direction_model.h5')


async def emit_fa_directions(sid):
    await asyncio.sleep(2)
    await sio.emit('data', {'direction': "left"}, room=sid, namespace='/esp32')
    await asyncio.sleep(0.5)
    await sio.emit('data', {'direction': "forward"}, room=sid, namespace='/esp32')
    await asyncio.sleep(2)
    await sio.emit('data', {'direction': "left"}, room=sid, namespace='/esp32')
    await asyncio.sleep(0.5)
    await sio.emit('data', {'direction': "forward"}, room=sid, namespace='/esp32')
    await asyncio.sleep(2)
    await sio.emit('data', {'direction': "stop"}, room=sid, namespace='/esp32')


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload_image")
async def upload_image(request: Request):
    global current_direction
    img_data = await request.body()
    filename = "image_to_process.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, 'wb') as f:
        f.write(img_data)

    # Run prediction in a separate thread to avoid blocking
    direction = await asyncio.to_thread(predict_arrow, filepath)

    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    if direction == "no_arrow":
        direction = "forward"
    await sio.emit('data', {'direction': direction, 'image': encoded_string}, namespace='/web')
    current_direction = direction
    return {'status': 'OK'}


@sio.on('connect', namespace='/web')
async def handle_web_connect(sid, environ):
    print('Web client connected')
    await sio.emit('connection_response', {'data': 'Web Connected'}, room=sid, namespace='/web')


@sio.on('disconnect', namespace='/web')
async def handle_web_disconnect(sid):
    print('Web client disconnected')


@sio.on('connect', namespace='/esp32')
async def handle_esp32_connect(sid, environ):
    print('ESP32 client connected')
    await sio.emit('connection_response', {'data': 'ESP32 Connected'}, room=sid, namespace='/esp32')
    asyncio.create_task(emit_fa_directions(sid))


@sio.on('disconnect', namespace='/esp32')
async def handle_esp32_disconnect(sid):
    print('ESP32 client disconnected')

app.mount("/", socket_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
