from telebot.handler_backends import State, StatesGroup

from utils.bot import telegram
from handlers import init_handlers

def error_handler(func):
    def wrapper(message, *args, **kwargs):
        try:
            return func(message, *args, **kwargs)
        except Exception as e:
            telegram.send_message(message.chat.id, 'An error occurred. Please try again later.')
            # Log the error
            print(f"Error: {e}")
    return wrapper

def start_command_handler(func):
    def wrapper(message, *args, **kwargs):
        if message.text == '/start':
            init_handlers.send_welcome(message)
            return
        else:
            return func(message, *args, **kwargs)
    return wrapper

def log_message_handler(func):
    def wrapper(message, *args, **kwargs):
        print(f"Handling message from {message.chat.id}: {message.text}")
        return func(message, *args, **kwargs)
    return wrapper