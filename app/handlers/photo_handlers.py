# handlers/image_handlers.py

from telebot import types
from .processing import process_images_and_send
from utils.bot import telegram, users_process_data
from decorators import start_command_handler, log_message_handler, error_handler

def get_image_file_id(message):
    """
    Checks if the message contains a photo or a document that is an image.
    Returns the file_id if a valid image is found, otherwise returns None.
    """
    if message.photo:
        return message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith('image/'):
        return message.document.file_id
    return None

def download_image(file_id, chat_id, file_name):
    file_info = telegram.get_file(file_id)
    downloaded_file = telegram.download_file(file_info.file_path)
    image_path = f'temp/{chat_id}_{file_name}.jpg'
    with open(image_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    return image_path

@start_command_handler
@log_message_handler
@error_handler
def process_image_type_step(message):
    chat_id = message.chat.id
    image_type = message.text
    users_process_data[chat_id] = {'image_type': image_type}

    prompt = ""
    if image_type == 'Exterior':
        prompt = "High-quality photo of the exterior of a building"
        msg = telegram.send_message(chat_id, "Please upload a photo of the exterior.")
        telegram.register_next_step_handler(msg, process_photo_upload)
    elif image_type == 'Interior':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('Kitchen', 'Living Room', 'Bathroom')  # Add more options as needed
        msg = telegram.send_message(chat_id, "What type of room are you interested in?", reply_markup=markup)
        telegram.register_next_step_handler(msg, process_room_type_step)
    
    users_process_data[chat_id]['prompt'] = prompt
    print(prompt)

@start_command_handler
@log_message_handler
@error_handler
def process_room_type_step(message):
    chat_id = message.chat.id
    room_type = message.text
    users_process_data[chat_id]['room_type'] = room_type

    prompt_map = {
        'Kitchen': "High-quality photo of the kitchen",
        'Living Room': "High-quality photo of the living room",
        'Bathroom': "High-quality photo of the bathroom"
    }
    prompt = prompt_map.get(room_type, "")
    users_process_data[chat_id]['prompt'] = prompt

    msg = telegram.send_message(chat_id, "Please upload a photo of the interior.")
    telegram.register_next_step_handler(msg, process_photo_upload)

@start_command_handler
@log_message_handler
@error_handler
def process_photo_upload(message):
    chat_id = message.chat.id

    file_id = get_image_file_id(message)
    if file_id is None:
        msg = telegram.reply_to(message, "This does not seem to be an image. Please upload an image directly. Image as a file or a link is not supported.")
        telegram.register_next_step_handler(msg, process_photo_upload)
        return
    
    image_path = download_image(file_id, chat_id, "image")
    users_process_data[chat_id]['image_path'] = image_path

    msg = telegram.send_message(chat_id, "Now, please upload a reference image.")
    telegram.register_next_step_handler(msg, process_reference_upload)

@start_command_handler
@log_message_handler
@error_handler
def process_reference_upload(message):
    chat_id = message.chat.id

    file_id = get_image_file_id(message)
    if file_id is None:
        msg = telegram.reply_to(message, "This does not seem to be an image. Please upload an image directly. Image as a file or a link is not supported.")
        telegram.register_next_step_handler(msg, process_reference_upload)
        return
    
    ref_image_path = download_image(file_id, chat_id, "ref_image")
    users_process_data[chat_id]['reference_image_path'] = ref_image_path

    telegram.reply_to(message, "Thank you! Processing your request...")
    prompt = users_process_data[chat_id].get('prompt', '')
    process_images_and_send(chat_id, users_process_data[chat_id]['image_path'], ref_image_path, prompt)
