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

bot_token = os.environ.get("TOKEN", "6665032973:AAEoRsnrvaAr0Vn3bgrizVaMjezo2Stlh7I")
api_hash = os.environ.get("HASH", "fcdc178451cd234e63faefd38895c991") 
api_id = os.environ.get("ID", "1923471")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)  


# handle ineex
def handleIndex(ele,message,msg):
    result = bypasser.scrapeIndex(ele)
    try: app.delete_messages(message.chat.id, msg.id)
    except: pass
    for page in result: app.send_message(message.chat.id, page, reply_to_message_id=message.id, disable_web_page_preview=True)


# loop thread
# loop thread
def loopthread(message):
    # Extracting caption text
    caption_text = message.text
    if caption_text is None:
        caption_text = message.caption

    if caption_text is None:
        app.send_message(message.chat.id, "⚠️ Please include a caption with the links.", reply_to_message_id=message.id)
        return
    
    # Finding links in the caption text
    urls = []
    for ele in caption_text.split():
        if "http://" in ele or "https://" in ele:
            urls.append(ele)
    
    if len(urls) == 0:
        app.send_message(message.chat.id, "⚠️ No valid links found in the caption.", reply_to_message_id=message.id)
        return

    msg = app.send_message(message.chat.id, "🔎 __bypassing...__", reply_to_message_id=message.id)

    links = ""
    for ele in urls:
        try:
            temp = bypasser.shortners(ele)
            print("bypassed:", temp)
            if temp is not None:
                links += temp + "\n\n"
        except Exception as e:
            print("Error:", e)
    
    app.delete_messages(message.chat.id, msg.id)
    final_message = f"{caption_text}\n\n{links}"
    if len(final_message) > 4096:
        app.send_message(message.chat.id, f"⚠️ The message is too long to be sent. Try sending fewer links.", reply_to_message_id=message.id)
    else:
        app.send_message(message.chat.id, final_message, reply_to_message_id=message.id, disable_web_page_preview=True)

# start command
@app.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, i am Link Bypasser Bot, just send me any supported links and i will you get you results.\nCheckout /help to Read More__",
    reply_markup=InlineKeyboardMarkup([
        [ InlineKeyboardButton("🌐 Source Code", url="https://github.com/bipinkrish/Link-Bypasser-Bot")],
        [ InlineKeyboardButton("Replit", url="https://replit.com/@bipinkrish/Link-Bypasser#app.py") ]]), 
        reply_to_message_id=message.id)


# help command
@app.on_message(filters.command(["help"]))
def send_help(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, HELP_TEXT, reply_to_message_id=message.id, disable_web_page_preview=True)


# links
@app.on_message(filters.text)
def receive(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bypass = Thread(target=lambda:loopthread(message),daemon=True)
    bypass.start()


# doc thread
def docthread(message):
    msg = app.send_message(message.chat.id, "🔎 __bypassing...__", reply_to_message_id=message.id)
    print("sent DLC file")
    file = app.download_media(message)
    dlccont = open(file,"r").read()
    links = bypasser.getlinks(dlccont)
    app.edit_message_text(message.chat.id, msg.id, f'__{links}__', disable_web_page_preview=True)
    remove(file)


# files
@app.on_message([filters.document,filters.photo,filters.video])
def docfile(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    try:
        if message.document.file_name.endswith("dlc"):
            bypass = Thread(target=lambda:docthread(message),daemon=True)
            bypass.start()
            return
    except: pass

    bypass = Thread(target=lambda:loopthread(message,True),daemon=True)
    bypass.start()


# server loop
print("Bot Starting")
app.run()
