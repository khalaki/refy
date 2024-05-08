import telebot
import config
from telebot import types
import os
from webui import StableDiffusionAPI, resize_image_to_max_dimension, load_and_prepare_payload

bot = telebot.TeleBot(config.TOKEN)
webui_server_url = config.API_ENDPOINT

users_process_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Exterior', 'Interior')
    msg = bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! Let's start! 💫\nPlease select the type of your base image.", reply_markup=markup)
    bot.register_next_step_handler(msg, process_image_type_step)

def process_image_type_step(message):
    chat_id = message.chat.id
    users_process_data[chat_id] = {'image_type': message.text}
    if message.text == 'Exterior':
        msg = bot.send_message(chat_id, "Please upload a photo of the exterior.")
        bot.register_next_step_handler(msg, process_photo_upload)
    elif message.text == 'Interior':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('Kitchen', 'Living Room', 'Bathroom')  # Add more options as needed
        msg = bot.send_message(chat_id, "What type of room are you interested in?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_room_type_step)

def process_room_type_step(message):
    chat_id = message.chat.id
    users_process_data[chat_id]['room_type'] = message.text  # This could be used for further customization
    msg = bot.send_message(chat_id, "Please upload a photo of the interior.")
    bot.register_next_step_handler(msg, process_photo_upload)

def process_photo_upload(message):
    chat_id = message.chat.id
    if not message.photo:
        msg = bot.reply_to(message, "This does not seem to be an image. Please upload an image.")
        bot.register_next_step_handler(msg, process_photo_upload)
        return
    
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    image_path = f'temp/{chat_id}_image.jpg'
    with open(image_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    users_process_data[chat_id]['image_path'] = image_path
    msg = bot.send_message(chat_id, "Now, please upload a reference image.")
    bot.register_next_step_handler(msg, process_reference_upload)

def process_reference_upload(message):
    chat_id = message.chat.id
    if not message.photo:
        msg = bot.reply_to(message, "This does not seem to be an image. Please upload an image.")
        bot.register_next_step_handler(msg, process_reference_upload)
        return
    
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    ref_image_path = f'temp/{chat_id}_ref_image.jpg'
    with open(ref_image_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, "Thank you! Processing your request...")
    process_images_and_send(chat_id, users_process_data[chat_id]['image_path'], ref_image_path)

def process_images_and_send(chat_id, image_path, ref_image_path):
    # This is a simplified version; you may want to handle this asynchronously in production

    output_dir = 'api_out'
    api_client = StableDiffusionAPI(webui_server_url, output_dir)
    payload_file_path = 'payload.json'

    payload = load_and_prepare_payload(payload_file_path, image_path, ref_image_path)
    api_client.call_img2img_api(**payload)
    
    
    # Identify all PNG images in the output directory
    image_files = [f for f in os.listdir(api_client.out_dir_i2i) if f.endswith('.png')]
    # Sort the files to ensure they are processed in a meaningful order
    sorted_image_files = sorted(image_files, key=lambda x: (int(x.split('-')[-1].split('.')[0]) if x.split('-')[-1].split('.')[0].isdigit() else float('inf'), x))

    # Send only the first four processed images back to the user
    for img_file in sorted_image_files[:4]:
        img_path = os.path.join(api_client.out_dir_i2i, img_file)
        with open(img_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)
    
    # Cleanup: Remove all images in the output directory after sending the first four
    for img_file in os.listdir(api_client.out_dir_i2i):
        os.remove(os.path.join(api_client.out_dir_i2i, img_file))

    # Also remove the uploaded images to prevent storage overflow
    os.remove(image_path)
    os.remove(ref_image_path)


if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    bot.polling(non_stop=True)
