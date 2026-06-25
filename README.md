# Image Steganography Tool

This project is a Python-based Information Security tool designed to demonstrate **Steganography** - the art of hiding information within other non-secret data (in this case, images).

## Core Triad Focus: Confidentiality
By hiding sensitive text strings directly inside the pixel array bytes of an image, we ensure that the communication remains covert. To a casual observer, the image looks perfectly normal.

## Features
- **Encode:** Hide secret text inside any PNG/JPG image (output is always PNG to preserve data).
- **Decode:** Extract hidden text from an encoded image.
- **Detect:** Scan a directory of images and identify those containing hidden messages using the tool's specific signature.
- **Sample Generation:** Create clean images for testing purposes.

## How it Works: LSB Steganography
The tool uses **Least Significant Bit (LSB)** steganography. Each pixel in an image is typically composed of three color channels: Red, Green, and Blue (RGB). Each channel is represented by 8 bits (0-255). 
The tool replaces the last bit (the least significant one) of these channels with bits from the secret message. Since the change is only 1/255th of the color value, it is virtually invisible to the human eye.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the tool:
   ```bash
   python main.py
   ```

## Usage
- Put your images in the `images/` folder.
- Use the menu-driven interface to hide, extract, or scan for data.
- Encoded images are saved with a `hidden_` prefix.


  The front-end of this project is served directly as a set of static files (inside the static folder, starting with
  index.html) by the backend app.py (which uses FastAPI).

  To run the web app and access the frontend, you need to start the FastAPI server:

  ### 1. Open your terminal and navigate to the project directory

    cd /home/shakeel/python/Info_Project

  ### 2. Activate the virtual environment

  Since the project has a  venv  directory, activate it:

    source venv/bin/activate

  ### 3. Run the FastAPI server using  uvicorn 

  Start the server with the reload option enabled:

    uvicorn app:app --reload

  ### 4. Access the Frontend

  Once the server starts running, open your web browser and go to:

  • http://127.0.0.1:8000/
  ──────
  Note: If you want to run the terminal-based interactive CLI version instead of the web version, you can run:

    python main.py
