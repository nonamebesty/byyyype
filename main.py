import pyrogram
from pyrogram import Client,filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from os import environ, remove
from threading import Thread
from json import load
from re import search

from texts import HELP_TEXT
import bypasser
import freewall
from time import time
import os

# bot
with open('config.json', 'r') as f: DATA = load(f)
def getenv(var): return environ.get(var) or DATA.get(var, None)

bot_token = os.environ.get("TOKEN", "6665032973:AAFotZ82R5GGhh--oVZ3jcKOSjOFzvfsums")
api_hash = os.environ.get("HASH", "fcdc178451cd234e63faefd38895c991") 
api_id = os.environ.get("ID", "1923471")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)  


# handle ineex
def handleIndex(ele,message,msg):
    result = bypasser.scrapeIndex(ele)
    try: app.delete_messages(message.chat.id, msg.id)
    except: pass
    for page in result: app.send_message(message.chat.id, page, reply_to_message_id=message.id, disable_web_page_preview=True)

# Assuming loopthread is defined somewhere else
    
# loop thread
# Revised loopthread with a default flag value
def loopthread(message, flag=False):
    texts = message.text or message.caption
    if not texts:
        app.send_message(message.chat.id, "⚠️ Please include a caption with the links.", reply_to_message_id=message.id)
        return

    if texts.startswith('/'):
        return  # Ignore command messages

    # Rest of your original loopthread code...

# Handle text messages
@app.on_message(filters.text & (lambda m: not m.get('entities') or m.get('entities')[0].get('type') != 'bot_command'))
def handle_text(client, message):
    bypass = Thread(target=lambda: loopthread(message, True), daemon=True)
    bypass.start()

# On message handler that did not include 'flag'
@app.on_message(filters.text)
def receive(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bypass = Thread(target=lambda: loopthread(message), daemon=True)
    bypass.start()

# Doc file handling where 'flag' might be needed
@app.on_message([filters.document,filters.photo,filters.video])
def docfile(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    try:
        if message.document and message.document.file_name.endswith("dlc"):
            bypass = Thread(target=lambda: docthread(message), daemon=True)
            bypass.start()
            return
    except AttributeError:
        pass  # Handle cases where message.document does not exist

    # For non-DLC documents or photos/videos, possibly needing flag
    bypass = Thread(target=lambda: loopthread(message, True), daemon=True)
    bypass.start()

# You might need to review other function calls for loopthread if they exist elsewhere in your code
# server loop
print("Bot Starting")
app.run()
