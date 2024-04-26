import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from os import environ, remove
from threading import Thread
from json import load
import os

# Bot configuration
with open('config.json', 'r') as f:
    DATA = load(f)

def getenv(var):
    return environ.get(var) or DATA.get(var, None)

bot_token = os.environ.get("TOKEN", "6665032973:AAFotZ82R5GGhh--oVZ3jcKOSjOFzvfsums")
api_hash = os.environ.get("HASH", "fcdc178451cd234e63faefd38895c991") 
api_id = os.environ.get("ID", "1923471")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)  

# Assuming bypasser and other modules are properly imported and implemented
import bypasser
import freewall

# Single definition of loopthread
def loopthread(message):
    texts = message.text or message.caption
    if not texts:
        app.send_message(message.chat.id, "⚠️ Please include a caption with the links.", reply_to_message_id=message.id)
        return

    if texts.startswith('/'):
        return  # Ignore commands

    lines = texts.split("\n")
    results = []
    processing_message = app.send_message(message.chat.id, "Processing links...", reply_to_message_id=message.id)

    for line in lines:
        if "http" in line and line.strip():
            link = line.split()[-1]
            caption = " ".join(line.split()[:-1])
            try:
                if bypasser.ispresent(bypasser.ddl.ddllist, link):
                    bypassed_link = bypasser.ddl.direct_link_generator(link)
                elif freewall.pass_paywall(link, check=True):
                    bypassed_link = freewall.pass_paywall(link) or "Failed to bypass"
                else:
                    bypassed_link = bypasser.shortners(link) or "Failed to bypass"
            except Exception as e:
                bypassed_link = f"Error: {str(e)}"
            results.append(f"{caption}\n{bypassed_link}\n")
        else:
            results.append(line)

    app.delete_messages(message.chat.id, processing_message.id)
    final_message = "\n".join(results)
    app.send_message(message.chat.id, final_message, disable_web_page_preview=True, reply_to_message_id=message.id)

# Correct usage of message filters
@app.on_message(filters.text & ~filters.command)
def handle_text(client, message):
    bypass = Thread(target=lambda: loopthread(message), daemon=True)
    bypass.start()

@app.on_message(filters.command(["start", "help"]))
def command_handler(client, message):
    if message.command[0] == "start":
        send_start(client, message)
    elif message.command[0] == "help":
        send_help(client, message)

def send_start(client, message):
    app.send_message(message.chat.id, "__👋 Hi there! Send me links and I'll try to bypass them.__",
                     reply_markup=InlineKeyboardMarkup([
                         [InlineKeyboardButton("🌐 Source Code", url="https://github.com/yourrepo")],
                         [InlineKeyboardButton("Replit", url="https://replit.com/@yourusername/yourproject")]]),
                     reply_to_message_id=message.id)

def send_help(client, message):
    app.send_message(message.chat.id, "Here's how to use me...", reply_to_message_id=message.id, disable_web_page_preview=True)

# Start the bot
print("Bot Starting")
app.run()
