# %%
from dotenv import load_dotenv
import os 
import telebot 
import datetime as dt 
import jdatetime 
import pymongo
import csv
from pymongo.errors import ConnectionFailure

# %%
# Get API token from a secure environment variable 

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_API_KEY')
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
        client.server_info()  # Will raise an exception if connection fails
        db = client["BidaramDB"]
        collection = db["UserInfo"]
        use_mongodb = True
        print("Successfully connected to MongoDB.")
    except ConnectionFailure:
        print("Failed to connect to MongoDB. Falling back to CSV.")
        use_mongodb = False
        setup_csv()

def setup_csv():
    if not os.path.exists(csv_filename):
        with open(csv_filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=csv_headers)
            writer.writeheader()
        print("CSV file created.")

# Initialize database connection or CSV
initialize_database()

# %%
# ... [Pagination class remains unchanged]

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
    print('------------------------------------------')
    global use_mongodb
    chat_id = message.chat.id
    current_datetime_persian = get_current_persian_datetime() 
    today_persian = jdatetime.datetime.now()
    time = today_persian.strftime("%Y-%m-%d %H:%M:%S")
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
    
    if use_mongodb:
        try:
            result = collection.insert_one(data)
            print("Data inserted successfully into MongoDB!")
        except pymongo.errors.PyMongoError as e:
            print("Error inserting into MongoDB:", e)
            use_mongodb = False
            setup_csv()
    
    if not use_mongodb:
        try:
            with open(csv_filename, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=csv_headers)
                writer.writerow(data)
            print("Data inserted successfully into CSV!")
        except IOError as e:
            print("Error writing to CSV:", e)
    
    bot.send_message(chat_id, reply_message)

@bot.message_handler(commands=['list'])
def handle_list(message):
    global use_mongodb
    list_msg = ""
    chat_id = message.chat.id
    username_code = message.from_user.id if message.from_user.id else "0" 
    
    if use_mongodb:
        query = {"UserID": username_code} 
        try:
            cursor = collection.find(query)
            for document in cursor:
                list_msg += '• ' + str(document["Time"]) + '\n'
        except pymongo.errors.PyMongoError as e:
            print("Error querying MongoDB:", e)
            use_mongodb = False
            list_msg = "Error retrieving data from the database. Switching to CSV."
    
    if not use_mongodb:
        try:
            with open(csv_filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["UserID"] == str(username_code):
                        list_msg += '• ' + row["Time"] + '\n'
        except IOError as e:
            print("Error reading from CSV:", e)
            list_msg = "Error retrieving data from the CSV file."

    if not list_msg:
        list_msg = "No data found for your user ID."
    
    bot.send_message(chat_id, list_msg)

@bot.message_handler(commands=['/'])
def handle_all(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Sorry, I don't understand that command. Try /help for a list of commands.")

if __name__ == "__main__":
    print('Bot started!')
    bot.infinity_polling()