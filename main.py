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
    texts = message.text or message.caption
    if not texts:
        app.send_message(message.chat.id, "⚠️ Please include a caption with the links.", reply_to_message_id=message.id)
        return

    lines = texts.split("\n")
    results = []
    processing_message = app.send_message(message.chat.id, "Processing links...", reply_to_message_id=message.id)

    # Process each line individually
    for line in lines:
        if "http" in line and line.strip():  # Check if the line contains an http link and is not just whitespace
            link = line.split()[-1]  # Assuming the link is the last part of the line
            caption = " ".join(line.split()[:-1])  # The rest is caption
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
            results.append(line)  # Include empty and non-empty lines as they are

    # Delete the processing message
    app.delete_messages(message.chat.id, processing_message.id)

    # Send the result message
    final_message = "\n".join(results)
    app.send_message(message.chat.id, final_message, disable_web_page_preview=True, reply_to_message_id=message.id)

# Handle text messages including those with photo captions
@app.on_message(filters.text)
def receive(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bypass = Thread(target=lambda: loopthread(message), daemon=True)
    bypass.start()

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
