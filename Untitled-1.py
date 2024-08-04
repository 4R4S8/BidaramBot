# %%
import os 
import telebot 
import datetime as dt 
import jdatetime 
import pymongo


# %%
# Get API token from a secure environment variable 
BOT_TOKEN = '7350608336:AAHgBaJR9Vqj2Bl6Mah6XMl_G6G9hPn1gHA' 
 
if not BOT_TOKEN: 
    raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable") 
 
bot = telebot.TeleBot(BOT_TOKEN) 

# %%
def get_current_persian_datetime(): 
    """Returns the current date and time in Persian format.""" 
    now_persian = jdatetime.datetime.now() 
    formatted_datetime = now_persian.strftime("%H:%M:%S | %A، %d %B %Y") 
    return formatted_datetime 

# %%
client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["BidaramDB"]
collection = db["UserInfo"]


# %%
class Pagination:
    def __init__(self, data, items_per_page):
        self.data = data
        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_pages = len(self.data) // self.items_per_page + 1  # Consider remainder

    def get_page_data(self):
        """Returns the data for the current page."""
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = min(self.current_page * self.items_per_page, len(self.data))
        return self.data[start_index:end_index]

    def create_message(self, chat_id):
        """Creates the message text for the current page."""
        page_data = self.get_page_data()
        message_text = "\n".join(page_data)  # Format data for each page
        return message_text

    def generate_buttons(self, chat_id):
        """Creates the button layout for pagination."""
        buttons = []
        if self.current_page > 1:
            buttons.append(
                telebot.types.InlineKeyboardButton("Prev", callback_data=f"prev_{chat_id}")
            )
        if self.current_page < self.total_pages:
            buttons.append(
                telebot.types.InlineKeyboardButton("Next", callback_data=f"next_{chat_id}")
            )
        return telebot.types.InlineKeyboardMarkup(row_width=1).add(*buttons)


# %%
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "سلام خوش اومدی ✨")
    
@bot.message_handler(commands=['help'])
def handle_start(message):
    chat_id = message.chat.id
    help_msg = "برای ثبت زمان بیدار شدن از دستور /bidaram استفاده کن"
    bot.send_message(chat_id, help_msg)

@bot.message_handler(commands=['bidaram'])
def handle_bidaram(message):
    chat_id = message.chat.id
    current_datetime_persian = get_current_persian_datetime() 
    today_persian = jdatetime.datetime.now()
    time = today_persian.strftime("%Y-%m-%d %H:%M:%S")
    # Get username (handle cases where it might be missing) 
    username = message.from_user.username if message.from_user.username else "Unknown User" 
 
    reply_message = f"⏰{current_datetime_persian}\n\n✨@{username}: {message.text}" 
    username_code = message.from_user.id if message.from_user.id else "0" 
    print_msg =  f"\n@{username}\nusernameCode :{username_code} \n\n {message.text}" 
    print(print_msg) 
    print("⏰ "+  time) 
    
    data = {
    "userName": username,
    "UserID": username_code,
    "Time": time}
    
    try:
        result = collection.insert_one(data)
        print("Data inserted successfully!")
    except pymongo.errors.PyMongoError as e:
        print("Error:", e)
    bot.send_message(chat_id, reply_message)

@bot.message_handler(commands=['list'])
def handle_list(message):
    list_msg = ""
    chat_id = message.chat.id
    username_code = message.from_user.id if message.from_user.id else "0" 
    query = {"UserID": username_code} 
    try:
        cursor = collection.find(query)
        for document in cursor:
            list_msg += '• ' + str(document["Time"]) + '\n'
    except pymongo.errors.PyMongoError as e:
        print("Error:", e)

    received_text = list_msg
    bot.send_message(chat_id, received_text)

@bot.message_handler(commands=['/'])
def handle_all(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Sorry, I don't understand that command. Try /help for a list of commands.")

if __name__ == "__main__":
    print('Connection established!')
    bot.infinity_polling()


