import os
import telebot
import datetime as dt
import jdatetime
import pymongo
import csv
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_API_KEY')
if not BOT_TOKEN:
    raise ValueError(f"{Fore.RED}Please set the TELEGRAM_BOT_TOKEN environment variable{Style.RESET_ALL}")

bot = telebot.TeleBot(BOT_TOKEN)

def get_current_persian_datetime():
    now_persian = jdatetime.datetime.now()
    formatted_datetime = now_persian.strftime("%H:%M:%S | %A، %d %B %Y")
    return formatted_datetime

# Global variables
use_mongodb = True
client = None
db = None
collection = None
csv_filename = "user_data.csv"
csv_headers = ["userName", "UserID", "Time"]

def initialize_database():
    global use_mongodb, client, db, collection
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client["BidaramDB"]
        collection = db["UserInfo"]
        use_mongodb = True
        print(f"{Fore.GREEN}Successfully connected to MongoDB.{Style.RESET_ALL}")
    except ConnectionFailure:
        print(f"{Fore.YELLOW}Failed to connect to MongoDB. Falling back to CSV.{Style.RESET_ALL}")
        use_mongodb = False
        setup_csv()

def setup_csv():
    if not os.path.exists(csv_filename):
        with open(csv_filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=csv_headers)
            writer.writeheader()
        print(f"{Fore.GREEN}CSV file created.{Style.RESET_ALL}")

# Initialize database connection or CSV
initialize_database()

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "سلام خوش اومدی ✨")
    print(f"{Fore.CYAN}User {message.from_user.username} started the bot.{Style.RESET_ALL}")

@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    reply_message = "برای ثبت زمان بیدار شدن از دستور /bidaram استفاده کن"
    bot.reply_to(message, reply_message)
    print(f"{Fore.CYAN}User {message.from_user.username} requested help.{Style.RESET_ALL}")

@bot.message_handler(commands=['bidaram'])
def handle_bidaram(message):
    print(f"\n{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}")
    global use_mongodb
    current_datetime_persian = get_current_persian_datetime()
    today_persian = jdatetime.datetime.now()
    time = today_persian.strftime("%Y-%m-%d %H:%M:%S")
    username = message.from_user.username if message.from_user.username else ""

    reply_message = f"⏰{current_datetime_persian}\n\n✨@{username}: {message.text}"
    username_code = message.from_user.id if message.from_user.id else "0"
    print(f"{Fore.CYAN}User: @{username}")
    print(f"User ID: {username_code}")
    print(f"Message: {message.text}")
    print(f"Time: {Fore.GREEN}⏰ {time}{Style.RESET_ALL}")

    data = {
        "userName": username,
        "UserID": username_code,
        "Time": time
    }

    if use_mongodb:
        try:
            result = collection.insert_one(data)
            print(f"{Fore.GREEN}Data inserted successfully into MongoDB!{Style.RESET_ALL}")
        except pymongo.errors.PyMongoError as e:
            print(f"{Fore.RED}Error inserting into MongoDB: {e}{Style.RESET_ALL}")
            use_mongodb = False
            setup_csv()

    if not use_mongodb:
        try:
            with open(csv_filename, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=csv_headers)
                writer.writerow(data)
            print(f"{Fore.GREEN}Data inserted successfully into CSV!{Style.RESET_ALL}")
        except IOError as e:
            print(f"{Fore.RED}Error writing to CSV: {e}{Style.RESET_ALL}")

    bot.reply_to(message, reply_message)

@bot.message_handler(commands=['list'])
def handle_list(message):
    global use_mongodb
    reply_message = ""
    chat_id = message.chat.id
    username_code = message.from_user.id if message.from_user.id else "0"
    
    print(f"\n{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}User {message.from_user.username} requested their list.{Style.RESET_ALL}")

    if use_mongodb:
        query = {"UserID": username_code}
        try:
            cursor = collection.find(query)
            for document in cursor:
                reply_message += '• ' + str(document["Time"]) + '\n'
            print(f"{Fore.GREEN}Data retrieved successfully from MongoDB.{Style.RESET_ALL}")
        except pymongo.errors.PyMongoError as e:
            print(f"{Fore.RED}Error querying MongoDB: {e}{Style.RESET_ALL}")
            use_mongodb = False
            reply_message = "Error retrieving data from the database. Switching to CSV."

    if not use_mongodb:
        try:
            with open(csv_filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["UserID"] == str(username_code):
                        reply_message += '• ' + row["Time"] + '\n'
            print(f"{Fore.GREEN}Data retrieved successfully from CSV.{Style.RESET_ALL}")
        except IOError as e:
            print(f"{Fore.RED}Error reading from CSV: {e}{Style.RESET_ALL}")
            reply_message = "Error retrieving data from the CSV file."

    if not reply_message:
        reply_message = "No data found for your user ID."
    
    bot.reply_to(message, reply_message)

@bot.message_handler(commands=['/'])
def handle_all(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Sorry, I don't understand that command. Try /help for a list of commands.")
    print(f"{Fore.YELLOW}User {message.from_user.username} used an unknown command.{Style.RESET_ALL}")

if __name__ == "__main__":
    print(f"{Fore.GREEN}{'=' * 50}")
    print(f"{Fore.GREEN}|{' ' * 18}Bot started!{' ' * 18}|")
    print(f"{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}")
    bot.infinity_polling()