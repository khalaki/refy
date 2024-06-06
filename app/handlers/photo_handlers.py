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

regenerate_message = None

#@start_command_handler
#@log_message_handler
#@error_handler
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

    try:
        process_images_and_send(chat_id, users_process_data[chat_id]['image_path'], ref_image_path, prompt)
    except Exception as e:
        print(f"Image processing error: {e}")
        # Retry button if processing failed
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Retry", callback_data=f"retry:{chat_id}:{users_process_data[chat_id]['image_path']}:{ref_image_path}:{prompt}"))
        telegram.send_message(chat_id, "Image processing failed. Please try again.", reply_markup=markup)
        return
    
    # Store necessary data for regeneration
    users_process_data[chat_id]["last_image_path"] = users_process_data[chat_id]['image_path']
    users_process_data[chat_id]["last_ref_image_path"] = ref_image_path
    users_process_data[chat_id]["last_prompt"] = prompt

    # Add "Regenerate" button
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Regenerate", callback_data=f"regenerate:{chat_id}"))
    global regenerate_message  # Use global variable
    regenerate_message = telegram.send_message(chat_id, "Images processed! Click below to regenerate with the same inputs.", reply_markup=markup)

@telegram.callback_query_handler(func=lambda call: call.data.startswith('regenerate:'))
def handle_regenerate_callback(call):
    chat_id = int(call.data.split(':')[1])

    if "last_image_path" not in users_process_data[chat_id]:
        telegram.answer_callback_query(call.id, "No previous image data found to regenerate.")
        return

    image_path = users_process_data[chat_id]["last_image_path"]
    ref_image_path = users_process_data[chat_id]["last_ref_image_path"]
    prompt = users_process_data[chat_id]["last_prompt"]
    
    # Acknowledge the callback and remove the button
    telegram.answer_callback_query(call.id, "Regenerating...")
    telegram.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)  # Remove the button

    # Indicate that regeneration is in progress
    new_message = telegram.send_message(chat_id, "Regenerating... Please wait.")
    
    # Process images again without a thread
    try:
        process_images_and_send(chat_id, image_path, ref_image_path, prompt)

        # Replace "Regenerating..." message with new regenerate button
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Regenerate", callback_data=f"regenerate:{chat_id}"))
        telegram.edit_message_text(
            chat_id=new_message.chat.id,
            message_id=new_message.message_id,
            text="Images processed! Click below to regenerate with the same inputs.",
            reply_markup=markup
        ) 

    except Exception as e:
        print(f"Image processing error: {e}")
        telegram.edit_message_text(
            chat_id=new_message.chat.id,
            message_id=new_message.message_id,
            text="Image processing failed. Please try again later."
        )