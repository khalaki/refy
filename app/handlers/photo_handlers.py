from .processing import process_images_and_send
from utils.bot import telegram, users_process_data

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