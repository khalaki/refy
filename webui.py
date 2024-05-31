from datetime import datetime
import urllib.request
import config
import base64
import json
import time
import os
from PIL import Image

class StableDiffusionAPI:
    def __init__(self, server_url, output_directory):
        self.server_url = server_url
        self.output_directory = output_directory
        self.out_dir_t2i = os.path.join(output_directory, 'txt2img')
        self.out_dir_i2i = os.path.join(output_directory, 'img2img')
        self.ensure_directories()

    def ensure_directories(self):
        os.makedirs(self.out_dir_t2i, exist_ok=True)
        os.makedirs(self.out_dir_i2i, exist_ok=True)

    @staticmethod
    def timestamp():
        return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")

    @staticmethod
    def encode_file_to_base64(path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')

    @staticmethod
    def decode_and_save_base64(base64_str, save_path):
        with open(save_path, "wb") as file:
            file.write(base64.b64decode(base64_str))

    def call_api(self, api_endpoint, **payload):
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(
            f'{self.server_url}/{api_endpoint}',
            headers={'Content-Type': 'application/json'},
            data=data,
        )
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))

    def call_txt2img_api(self, **payload):
        response = self.call_api('sdapi/v1/txt2img', **payload)
        for index, image in enumerate(response.get('images')):
            save_path = os.path.join(self.out_dir_t2i, f'txt2img-{self.timestamp()}-{index}.png')
            self.decode_and_save_base64(image, save_path)

    def call_img2img_api(self, **payload):
        response = self.call_api('sdapi/v1/img2img', **payload)
        for index, image in enumerate(response.get('images')):
            save_path = os.path.join(self.out_dir_i2i, f'img2img-{self.timestamp()}-{index}.png')
            self.decode_and_save_base64(image, save_path)

def resize_image_to_max_dimension(image_path, max_dimension=768):
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        scaling_factor = max_dimension / max(original_width, original_height)
        return int(original_width * scaling_factor), int(original_height * scaling_factor)

def load_and_prepare_payload(file_path, image_path, ref_image_path):
    with open(file_path, 'r') as file:
        payload = json.load(file)

    new_width, new_height = resize_image_to_max_dimension(image_path)
    encoded_ref_image = StableDiffusionAPI.encode_file_to_base64(ref_image_path)
    payload['init_images'] = [StableDiffusionAPI.encode_file_to_base64(image_path)]
    payload['height'] = new_height
    payload['width'] = new_width
    payload['batch_size'] = 1
    payload['alwayson_scripts']['ControlNet']['args'][1]['image']['image'] = encoded_ref_image
    payload['alwayson_scripts']['ControlNet']['args'][1]['image']['mask'] = None

    return payload

def main():
    webui_server_url = config.API_ENDPOINT
    output_dir = 'api_out'
    api_client = StableDiffusionAPI(webui_server_url, output_dir)

    payload_file_path = 'payload.json'
    image_path = "temp/image.png"
    ref_image_path = "temp/ref_image.jpg"

    payload = load_and_prepare_payload(payload_file_path, image_path, ref_image_path)

    ### debug mode
    output_payload_file_path = 'payload_output.json'
    with open(output_payload_file_path, 'w') as file:
        json.dump(payload, file, indent=4)
    ###

    api_client.call_img2img_api(**payload)

if __name__ == '__main__':
    main()
