from telebot import types

from .processing import process_images_and_send
from utils.bot import telegram, users_process_data
from decorators import start_command_handler, log_message_handler, error_handler

@start_command_handler
@log_message_handler
@error_handler
def process_image_type_step(message):
  chat_id = message.chat.id
  users_process_data[chat_id] = {'image_type': message.text}

  if message.text == 'Exterior':
    msg = telegram.send_message(chat_id, "Please upload a photo of the exterior.")
    telegram.register_next_step_handler(msg, process_photo_upload)
  elif message.text == 'Interior':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Kitchen', 'Living Room', 'Bathroom')  # Add more options as needed
    msg = telegram.send_message(chat_id, "What type of room are you interested in?", reply_markup=markup)
    telegram.register_next_step_handler(msg, process_room_type_step)

@start_command_handler
@log_message_handler
@error_handler
def process_room_type_step(message):
  chat_id = message.chat.id

  users_process_data[chat_id]['room_type'] = message.text  # This could be used for further customization
  msg = telegram.send_message(chat_id, "Please upload a photo of the interior.")
  telegram.register_next_step_handler(msg, process_photo_upload)

@start_command_handler
@log_message_handler
@error_handler
def process_photo_upload(message):
    chat_id = message.chat.id

    if not message.photo:
        msg = telegram.reply_to(message, "This does not seem to be an image. Please upload an image.")
        telegram.register_next_step_handler(msg, process_photo_upload)
        return
    
    file_id = message.photo[-1].file_id
    file_info = telegram.get_file(file_id)
    downloaded_file = telegram.download_file(file_info.file_path)
    
    image_path = f'temp/{chat_id}_image.jpg'
    with open(image_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    users_process_data[chat_id]['image_path'] = image_path
    msg = telegram.send_message(chat_id, "Now, please upload a reference image.")
    telegram.register_next_step_handler(msg, process_reference_upload)

@start_command_handler
@log_message_handler
@error_handler
def process_reference_upload(message):
    chat_id = message.chat.id
    if not message.photo:
        msg = telegram.reply_to(message, "This does not seem to be an image. Please upload an image.")
        telegram.register_next_step_handler(msg, process_reference_upload)
        return
    
    file_id = message.photo[-1].file_id
    file_info = telegram.get_file(file_id)
    downloaded_file = telegram.download_file(file_info.file_path)
    
    ref_image_path = f'temp/{chat_id}_ref_image.jpg'
    with open(ref_image_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    telegram.reply_to(message, "Thank you! Processing your request...")
    process_images_and_send(chat_id, users_process_data[chat_id]['image_path'], ref_image_path)