from PIL import Image

def resize_image_to_max_dimension(image_path, max_dimension=768):
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        scaling_factor = max_dimension / max(original_width, original_height)
        return int(original_width * scaling_factor), int(original_height * scaling_factor)