# Telegram Bot Project

This project is a Telegram bot that guides users through a process of selecting image types, uploading photos, and handling reference images. The bot uses the `pyTelegramBotAPI` library and is structured to ensure maintainability and scalability.

## Project Structure

```
my_project/
├── config.py
├── main.py
├── handlers/
│ ├── init.py
│ ├── start_handler.py
│ ├── image_handlers.py
│ ├── ...
└── decorators.py
```

- **config.py**: Contains the bot configuration and global variables.
- **main.py**: The entry point of the bot, starts the polling.
- **handlers/**: Directory containing handler modules for different functionalities.
  - **start_handler.py**: Handles the `/start` command.
  - **image_handlers.py**: Handles image type selection and photo uploads.
- **decorators.py**: Contains decorators for handling common tasks across multiple handlers.

## Setup

### Prerequisites

- Python 3.7+
- `pyTelegramBotAPI` library

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. Install the required libraries:
    ```sh
    pip install pyTelegramBotAPI
    ```

3. Create a `secrets.py` file in the root directory:
    ```python
    # secrets.py
    BOT_TOKEN = 'your-telegram-bot-token-here'
    ```

## Usage

1. **Configure the Bot**:
   - Update `secrets.py` with your Telegram bot token.

2. **Run the Bot**:
   ```sh
   python main.py
   ```

## Adding New Handlers
1. Create a new file in the handlers/ directory.
2. Define your handler function(s) and apply necessary decorators.
3. Ensure the new handler file is imported in handlers/__init__.py.
## Conclusion
This project structure and code organization help keep your bot scalable and maintainable. By separating concerns into different modules and using decorators, you can efficiently manage complex bot functionalities.