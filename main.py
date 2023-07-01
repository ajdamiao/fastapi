from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
import os
import uuid
from rembg import remove
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from starlette.routing import request_response
from fastapi.responses import FileResponse

u2net_model_path = "/auxs/u2net.onnx"

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

def removeBackground(image_data):
    img_removed = remove(image_data, u2net_model_path)
    image_removed_filename = str(uuid.uuid4()) + '.jpg'
    image_removed_path = os.path.join('out', image_removed_filename)
    with open(image_removed_path, 'wb') as f:
        f.write(img_removed)

    return image_removed_path

@app.get('/')
def home():
    return {"message": "Hello, World!"}

@app.put('/process-image')
async def process_image(request: Request, image: UploadFile = File(...)):
    image_data = await image.read()
    try:
        # Chama a função removeBackground()
        image_removed_path = removeBackground(image_data)
    except Exception as e:
        return {'error': str(e)}

    image_removed_filename = os.path.basename(image_removed_path)
    url_path = app.url_path_for('output_image', path=image_removed_filename)
    image_url = str(request.base_url.include_query_params()).replace(request.url.path, '') + url_path
    return {'image_url': image_url}

@app.get('/output/{path:path}')
def output_image(path):
    return FileResponse(os.path.join('in', path), media_type='image/jpeg')

@app.get('/list-files')
def list_files():
    output_directory = 'out'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    files = os.listdir(output_directory)
    return {'files': files}
