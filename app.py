import io
import os

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from steganography import encode_image, decode_image, detect_steganography

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


async def read_upload(file: UploadFile) -> bytes:
    """Reads an uploaded file into memory, enforcing a size cap and extension allowlist."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid image format. Only PNG, JPG, JPEG are supported.")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"Image too large. Max size is {MAX_UPLOAD_SIZE // (1024 * 1024)}MB.")

    return contents


@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyzes an uploaded image for hidden data using steganography.detect_steganography.
    """
    contents = await read_upload(file)
    try:
        is_hidden, decoded_message = detect_steganography(io.BytesIO(contents))
        return {"is_hidden": is_hidden, "decoded_message": decoded_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {e}")


@app.post("/encode_image")
async def encode_image_api(file: UploadFile = File(...), secret_message: str = Form(...)):
    """
    Hides a secret message within an uploaded image using steganography.encode_image
    and streams the resulting PNG back in memory (no disk writes).
    """
    contents = await read_upload(file)

    output_buffer = io.BytesIO()
    output_buffer.name = "encoded.png"  # lets Pillow infer PNG format on save()

    try:
        encode_image(io.BytesIO(contents), secret_message, output_buffer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding image: {e}")

    output_buffer.seek(0)
    return StreamingResponse(output_buffer, media_type="image/png")


@app.post("/decode_image")
async def decode_image_api(file: UploadFile = File(...)):
    """
    Extracts a hidden message from an uploaded image using steganography.decode_image.
    """
    contents = await read_upload(file)
    try:
        decoded_message = decode_image(io.BytesIO(contents))
        if decoded_message:
            return {"decoded_message": decoded_message, "message": "Message extracted successfully."}
        else:
            return {"decoded_message": None, "message": "No hidden message found or incorrect format."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decoding image: {e}")


@app.post("/generate_sample")
async def generate_sample_image_api():
    """
    Generates a clean sample image for testing and streams it back in memory.
    """
    try:
        from PIL import Image, ImageDraw

        img = Image.new('RGB', (350, 350), color=(31, 41, 55))
        d = ImageDraw.Draw(img)
        d.rectangle([(20, 20), (330, 330)], outline=(59, 130, 246), width=2)
        d.text((50, 150), "Clean Image for Steganography", fill=(243, 244, 246))
        d.text((50, 180), "Ready for hidden message", fill=(156, 163, 175))

        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        return StreamingResponse(output_buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample image: {e}")


# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")
