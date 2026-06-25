import os
import shutil
import uuid
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
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

# Directory to store uploaded and processed images temporarily
# Ensure this directory exists and is writable
TEMP_IMAGE_DIR = "temp_images"
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def get_image_path(image_id: str) -> str:
    """Constructs the full path for a given image ID."""
    return os.path.join(TEMP_IMAGE_DIR, f"{image_id}.png") # Assuming all processed images are PNG

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    """
    Uploads an image file, saves it temporarily, and returns a unique ID.
    """
    try:
        image_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in [".png", ".jpg", ".jpeg"]:
            raise HTTPException(status_code=400, detail="Invalid image format. Only PNG, JPG, JPEG are supported.")

        temp_path = os.path.join(TEMP_IMAGE_DIR, f"{image_id}{file_extension}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Convert to PNG for consistent processing later, if it's not already
        if file_extension != ".png":
            from PIL import Image
            img = Image.open(temp_path)
            png_path = get_image_path(image_id)
            img.save(png_path)
            os.remove(temp_path) # Remove original non-PNG file
        else:
            png_path = temp_path # If already PNG, just use its path

        return {"image_id": image_id, "filename": file.filename, "image_url": f"/images/{image_id}.png"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {e}")

@app.get("/images/{image_id}.png")
async def get_image(image_id: str):
    """Serves an image file from the temporary directory."""
    image_path = get_image_path(image_id)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(image_path, media_type="image/png")


@app.post("/analyze_image")
async def analyze_image(image_id: str):
    """
    Analyzes an image for hidden data using steganography.detect_steganography.
    """
    image_path = get_image_path(image_id)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    
    try:
        is_hidden, decoded_message = detect_steganography(image_path)
        return {"image_id": image_id, "is_hidden": is_hidden, "decoded_message": decoded_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {e}")

@app.post("/encode_image")
async def encode_image_api(image_id: str, secret_message: str):
    """
    Hides a secret message within an image using steganography.encode_image.
    """
    input_image_path = get_image_path(image_id)
    if not os.path.exists(input_image_path):
        raise HTTPException(status_code=404, detail="Original image not found.")
    
    encoded_image_id = str(uuid.uuid4())
    output_image_path = get_image_path(encoded_image_id)
    
    try:
        encode_image(input_image_path, secret_message, output_image_path)
        return {"encoded_image_id": encoded_image_id, "message": "Message hidden successfully.", "image_url": f"/images/{encoded_image_id}.png"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding image: {e}")

@app.post("/decode_image")
async def decode_image_api(image_id: str):
    """
    Extracts a hidden message from an image using steganography.decode_image.
    """
    image_path = get_image_path(image_id)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    
    try:
        decoded_message = decode_image(image_path)
        if decoded_message:
            return {"image_id": image_id, "decoded_message": decoded_message, "message": "Message extracted successfully."}
        else:
            return {"image_id": image_id, "decoded_message": None, "message": "No hidden message found or incorrect format."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decoding image: {e}")

@app.delete("/delete_image/{image_id}")
async def delete_image(image_id: str):
    """
    Deletes an image from the temporary storage.
    """
    image_path = get_image_path(image_id)
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
            return {"message": f"Image {image_id} deleted successfully."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting image: {e}")
    else:
        raise HTTPException(status_code=404, detail="Image not found.")

@app.post("/generate_sample")
async def generate_sample_image_api():
    """
    Generates a clean sample image for testing.
    """
    try:
        from PIL import Image, ImageDraw
        image_id = str(uuid.uuid4())
        png_path = get_image_path(image_id)
        
        # Create a simple clean image
        img = Image.new('RGB', (350, 350), color=(31, 41, 55))
        d = ImageDraw.Draw(img)
        d.rectangle([(20, 20), (330, 330)], outline=(59, 130, 246), width=2)
        d.text((50, 150), "Clean Image for Steganography", fill=(243, 244, 246))
        d.text((50, 180), "Ready for hidden message", fill=(156, 163, 175))
        img.save(png_path)
        
        return {"image_id": image_id, "filename": "sample.png", "image_url": f"/images/{image_id}.png"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample image: {e}")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")
