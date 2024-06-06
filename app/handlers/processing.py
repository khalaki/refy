import os
import config
from utils.bot import telegram
from utils.api import StableDiffusionAPI
from utils.payload_utils import load_and_prepare_payload


def process_images_and_send(chat_id, image_path, ref_image_path, prompt):
    # This is a simplified version; you may want to handle this asynchronously in production

    output_dir = 'api_out'
    api_client = StableDiffusionAPI(config.WEBUI_SERVER_URL, config.OUTPUT_DIR)
    payload_file_path = 'payload.json'

    payload = load_and_prepare_payload(payload_file_path, image_path, ref_image_path, prompt)
    api_client.call_img2img_api(**payload)
    
    
    # Identify all PNG images in the output directory
    image_files = [f for f in os.listdir(api_client.out_dir_i2i) if f.endswith('.png')]
    # Sort the files to ensure they are processed in a meaningful order
    sorted_image_files = sorted(image_files, key=lambda x: (int(x.split('-')[-1].split('.')[0]) if x.split('-')[-1].split('.')[0].isdigit() else float('inf'), x))

    # Send only the first four processed images back to the user
    for img_file in sorted_image_files[:4]:
        img_path = os.path.join(api_client.out_dir_i2i, img_file)
        with open(img_path, 'rb') as photo:
          telegram.send_photo(chat_id, photo)
    
    # Cleanup: Remove all images in the output directory after sending the first four
    for img_file in os.listdir(api_client.out_dir_i2i):
        os.remove(os.path.join(api_client.out_dir_i2i, img_file))

    # Also remove the uploaded images to prevent storage overflow
    os.remove(image_path)
    os.remove(ref_image_path)