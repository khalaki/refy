from datetime import datetime
import urllib.request
import base64
import json
import time
import os

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