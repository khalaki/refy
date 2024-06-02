from app import config
from app.utils import api, payload_utils
import json

def debug():
    webui_server_url = config.WEBUI_SERVER_URL
    output_dir = config.OUTPUT_DIR
    api_client = api.StableDiffusionAPI(webui_server_url, output_dir)

    payload_file_path = config.PAYLOAD_FILE_PATH
    image_path = "temp/image.png"
    ref_image_path = "temp/ref_image.jpg"

    payload = payload_utils.load_and_prepare_payload(payload_file_path, image_path, ref_image_path)

    ### debug mode
    output_payload_file_path = 'payload_output.json'
    with open(output_payload_file_path, 'w') as file:
        json.dump(payload, file, indent=4)
    ###
    # Comment out in debug mode if you don't want to call the API
    api_client.call_img2img_api(**payload)
    

if __name__ == '__debug__':
    debug()