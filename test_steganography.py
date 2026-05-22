import os
from steganography import encode_image, decode_image, detect_steganography
from PIL import Image

def test_steganography():
    test_img = "test_image.png"
    output_img = "test_hidden.png"
    secret_message = "This is a secret message!"
    
    # 1. Create a dummy image
    img = Image.new('RGB', (50, 50), color='red')
    img.save(test_img)
    print(f"Created test image: {test_img}")
    
    # 2. Encode
    encode_image(test_img, secret_message, output_img)
    
    # 3. Decode
    decoded = decode_image(output_img)
    print(f"Decoded message: {decoded}")
    
    assert decoded == secret_message, "Decoding failed!"
    print("Test Passed: Encoding and Decoding works!")
    
    # 4. Detection
    is_hidden, msg = detect_steganography(output_img)
    assert is_hidden == True
    assert msg == secret_message
    print("Test Passed: Detection works!")
    
    is_hidden_clean, _ = detect_steganography(test_img)
    assert is_hidden_clean == False
    print("Test Passed: Clean image detection works!")
    
    # Cleanup
    os.remove(test_img)
    os.remove(output_img)
    print("Cleanup done.")

if __name__ == "__main__":
    test_steganography()
