import os
import sys
from steganography import encode_image, decode_image, detect_steganography
from PIL import Image, ImageDraw

IMAGE_DIR = "images"

def setup_environment():
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        print(f"Created directory: {IMAGE_DIR}")

def create_sample_image(filename="sample.png"):
    """Creates a simple clean image for testing."""
    path = os.path.join(IMAGE_DIR, filename)
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Clean Image", fill=(255, 255, 0))
    img.save(path)
    print(f"Created sample clean image: {path}")
    return path

def list_images():
    files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        print("No images found in images/ folder.")
    return files

def main():
    setup_environment()
    
    while True:
        print("\n--- Image Steganography Tool ---")
        print("1. Hide Message in Image")
        print("2. Extract Message from Image")
        print("3. Scan 'images/' folder for Hidden Data")
        print("4. Create Sample Clean Image")
        print("5. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            images = list_images()
            if not images: continue
            
            for i, img in enumerate(images):
                print(f"{i+1}. {img}")
            
            img_choice = int(input("Select image index: ")) - 1
            input_path = os.path.join(IMAGE_DIR, images[img_choice])
            
            message = input("Enter secret message: ")
            output_name = "hidden_" + images[img_choice]
            if not output_name.endswith('.png'):
                output_name = output_name.rsplit('.', 1)[0] + ".png" # PNG is better for LSB
            
            output_path = os.path.join(IMAGE_DIR, output_name)
            
            try:
                encode_image(input_path, message, output_path)
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '2':
            images = list_images()
            if not images: continue
            
            for i, img in enumerate(images):
                print(f"{i+1}. {img}")
            
            img_choice = int(input("Select image index: ")) - 1
            input_path = os.path.join(IMAGE_DIR, images[img_choice])
            
            message = decode_image(input_path)
            if message:
                print(f"Hidden Message Found: {message}")
            else:
                print("No hidden message found or incorrect format.")
                
        elif choice == '3':
            images = list_images()
            print("\nScanning images for potential hidden data...")
            for img_name in images:
                path = os.path.join(IMAGE_DIR, img_name)
                is_hidden, msg = detect_steganography(path)
                status = "[MALICIOUS/HIDDEN]" if is_hidden else "[CLEAN]"
                print(f"{status} {img_name}")
                if is_hidden:
                    print(f"   -> Secret Content: {msg}")
                    
        elif choice == '4':
            name = input("Enter filename (e.g., test.png): ")
            create_sample_image(name)
            
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
