import json
from .image_tools import resize_image_to_max_dimension
from .api import StableDiffusionAPI

def load_and_prepare_payload(file_path, image_path, ref_image_path, prompt):
    with open(file_path, 'r') as file:
        payload = json.load(file)

    new_width, new_height = resize_image_to_max_dimension(image_path)
    encoded_ref_image = StableDiffusionAPI.encode_file_to_base64(ref_image_path)
    payload['init_images'] = [StableDiffusionAPI.encode_file_to_base64(image_path)]
    payload['height'] = new_height
    payload['width'] = new_width
    payload['batch_size'] = 1
    payload['prompt'] = f"{prompt}, best quality, <lora:more_details:0.5> <lora:SDXLrender_v2.0:1>"
    payload['alwayson_scripts']['ControlNet']['args'][1]['image']['image'] = encoded_ref_image
    payload['alwayson_scripts']['ControlNet']['args'][1]['image']['mask'] = None

    output_payload_file_path = 'payload_output.json'
    with open(output_payload_file_path, 'w') as file:
        json.dump(payload, file, indent=4)
    ###

    return payload