from telebot import types
from .photo_handlers import process_photo_upload
from utils.bot import telegram, users_process_data

@telegram.message_handler(commands=['start'])
def send_welcome(message):
  chat_id = message.chat.id
  users_process_data[chat_id] = {}

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  markup.add('Exterior', 'Interior')
  msg = telegram.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! Let's start! 💫\nPlease select the type of your base image.", reply_markup=markup)
  telegram.register_next_step_handler(msg, process_image_type_step)

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

def process_room_type_step(message):
  chat_id = message.chat.id

  users_process_data[chat_id]['room_type'] = message.text  # This could be used for further customization
  msg = telegram.send_message(chat_id, "Please upload a photo of the interior.")
  telegram.register_next_step_handler(msg, process_photo_upload)