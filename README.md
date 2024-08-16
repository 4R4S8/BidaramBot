# 🌅 Bidaram Telegram Bot

## 📖 Overview

Bidaram (meaning "I'm awake" in Persian) is a Telegram bot designed to help users track their wake-up times. It's perfect for those who want to maintain a consistent sleep schedule or simply log their daily routines.

## ✨ Features

- 🕰️ Record wake-up times with a simple command
- 📊 View your wake-up history
- 🇮🇷 Supports Persian (Jalali) calendar
- 💾 Flexible data storage (MongoDB or CSV)
- 🎨 Colorful console output for easy monitoring

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip
- MongoDB (optional)

### Installation

1. Clone the repository:

  `git clone https://github.com/yourusername/bidaram-bot.git`
  
  `cd bidaram-bot`


2. Create a virtual environment:

`python -m venv bidaram-env`

`source bidaram-env/bin/activate  # On Windows use bidaram-env\Scripts\activate`


3. Install the required packages:

`pip install -r requirements.txt`


5. Create a `.env` file in the project root and add your Telegram Bot Token:
BOT_API_KEY=your_telegram_bot_token_here


### Usage

Run the bot:

`python bidaram_bot.py`


## 🤖 Bot Commands

- `/start` - Start the bot
- `/help` - Display help information
- `/bidaram` - Record your wake-up time
- `/list` - View your wake-up history

## 🗄️ Data Storage

The bot supports two storage options:

1. **MongoDB** (default): Stores user data in a MongoDB database.
2. **CSV**: Falls back to CSV storage if MongoDB is unavailable.

## 🛠️ Configuration

Edit the `bidaram_bot.py` file to customize:

- MongoDB connection string
- CSV file name
- Date and time formats

## 📊 Logging

The bot uses colorful console output for easy monitoring:

- 🟢 Green: Successful operations
- 🔵 Blue: User actions
- 🟡 Yellow: Warnings
- 🔴 Red: Errors

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- [jdatetime](https://github.com/slashmili/python-jalali)
- [pymongo](https://github.com/mongodb/mongo-python-driver)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [colorama](https://github.com/tartley/colorama)

---

Made with ❤️ by 4R4S8
