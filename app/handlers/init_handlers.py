from telebot import types
from .photo_handlers import process_image_type_step
from utils.bot import telegram, users_process_data
from decorators import log_message_handler, error_handler

@telegram.message_handler(commands=['start'])
@log_message_handler
@error_handler
def send_welcome(message):
  chat_id = message.chat.id
  users_process_data[chat_id] = {}

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  markup.add('Exterior', 'Interior', 'Artwork')
  msg = telegram.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! Let's start! 💫\nPlease select the type of your base image.", reply_markup=markup)
  telegram.register_next_step_handler(msg, process_image_type_step)