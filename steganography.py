from PIL import Image
import binascii

# Delimiter to mark the end of the hidden message
DELIMITER = "###END###"

def text_to_bin(text):
    """Convert text string to a string of bits."""
    return bin(int(binascii.hexlify(text.encode()), 16))[2:].zfill(8 * len(text))

def bin_to_text(bits):
    """Convert a string of bits back to text."""
    try:
        n = int(bits, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    except Exception:
        return None

def encode_image(image_path, text, output_path):
    """Hide text inside an image using LSB."""
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    encoded_text = text + DELIMITER
    binary_data = ''.join(format(ord(c), '08b') for c in encoded_text)
    
    pixels = list(img.getdata())
    if len(binary_data) > len(pixels) * 3:
        raise ValueError("Text too long to hide in this image.")
    
    new_pixels = []
    bit_idx = 0
    
    for pixel in pixels:
        pixel = list(pixel)
        for i in range(3): # R, G, B
            if bit_idx < len(binary_data):
                # Replace the LSB with our data bit
                pixel[i] = (pixel[i] & ~1) | int(binary_data[bit_idx])
                bit_idx += 1
        new_pixels.append(tuple(pixel))
    
    img.putdata(new_pixels)
    img.save(output_path)
    print(f"Success: Message hidden in {output_path}")

def decode_image(image_path):
    """Extract hidden text from an image."""
    img = Image.open(image_path)
    pixels = list(img.getdata())
    
    binary_data = ""
    for pixel in pixels:
        for val in pixel[:3]:
            binary_data += str(val & 1)
    
    # Split into bytes and convert to characters
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_text = ""
    for b in all_bytes:
        try:
            char = chr(int(b, 2))
            decoded_text += char
            if DELIMITER in decoded_text:
                return decoded_text.replace(DELIMITER, "")
        except ValueError:
            break
            
    return None

def detect_steganography(image_path):
    """
    Check if an image likely contains hidden data.
    This is a basic heuristic: it tries to decode and looks for the delimiter.
    In a real-world scenario, steganalysis is more complex.
    """
    decoded = decode_image(image_path)
    if decoded is not None:
        return True, decoded
    return False, None
