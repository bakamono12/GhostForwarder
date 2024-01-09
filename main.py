import asyncio
import time
import os
from generate_thumb import extract_screenshot
import random
import logging
from pyrogram import Client, filters

# session string from auth.py
session_string = os.environ.get("SESSION_STRING", None)
group_id = os.environ.get("GROUP", None)
# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read the chat's list file and store it in a list
my_dir = os.getcwd()
os.chmod(my_dir, 0o777)
os.chmod(my_dir + '/' + 'my_chats.txt', 0o777)
try:
    file = open(file=my_dir + '/' + 'my_chats.txt', mode='r+', encoding='utf-8')
except FileNotFoundError:
    file = open(file=my_dir + '/' + 'my_chats.txt', mode='w+', encoding='utf-8')

# chat ids
MY_CHAT = file.read().split()

# New instance of Client
# In future we will use session string as the environment var
bot = Client("ghost-forwarder", session_string=session_string)


def check_owner(func):
    async def wrapper(client, message):
        if client.me.id == message.from_user.id:
            await func(client, message)
        else:
            # log in logger if unauthorized user detected
            # print("Unauthorized access from user: %s" % message.from_user.id)
            logger.warning(
                "Unauthorized access from user: %s - %s" % (message.from_user.first_name, message.from_user.id))

    return wrapper


@bot.on_message(filters.command("boomer"))
@check_owner
async def start(client, message):
    # Random greetings for the user
    greetings = ["Hello", "Hi", "Hey", "Hiya", "Howdy", "Hola", "Bonjour", "Ciao", "Salut", "Hallo"]
    greet = random.choice(greetings)
    await message.reply_text(
        "%s %s,\nI am Ghost Forwarder. I can forward messages from private chat that doesn't allow forward "
        "to another chats. \n\n"
        "To get started, send `/help` to know more." % (greet, message.from_user.first_name),
        reply_to_message_id=message.id
    )


# # help command
@bot.on_message(filters.command("help"))
@check_owner
async def helper(client, message):
    await message.reply_text(
        "I am Ghost Forwarder. I can forward messages from one chat to another. \n\n"
        "To get started, send `/chats` to set the chat_id for sources.\n"
        "To get the current Chat ID send `/get_chat_id` in any chat to get chat_id.\n"
        "These will be Used for triggering the forwarding.\nIn Case you don't add any chat_id I'll send a reminder "
        "in your Saved Messages.\n"
        "Send `/chats` {chat_id(s)} to set the source chat.\n"
        "Example: `/chats 123456789` OR `/source_chat 12345678 12121233`\n",
        reply_to_message_id=message.id)


@bot.on_message(filters.command("chats"))
@check_owner
async def set_source_chats(client, message):
    source_chat_selected = message.text.split()
    source_chat = open(file=my_dir + '/' + 'my_chats.txt', mode='a+', encoding='utf-8')
    if len(source_chat_selected) > 1:
        source_chat_ids = [int(chat_id) for chat_id in source_chat_selected[1:] if is_valid_chat_id(chat_id)]
        if source_chat_ids:
            for chat_id in source_chat_ids:
                if chat_id not in MY_CHAT:
                    source_chat.write(str(chat_id) + '\n')
                    MY_CHAT.append(chat_id)
            await message.reply_text(
                f"Source Chat has been set to {source_chat_ids}",
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                "Invalid chat ID(s) provided. Please provide one or more valid chat IDs.\nTo get the current Chat ID "
                "send `/get_chat_id` in any chat to get chat_id.",
                reply_to_message_id=message.id
            )
    else:
        await message.reply_text(
            "Send `/chats` {chat_id(s)} to set the source chat. \n\n"
            "Example: `/chats 123456789` OR `/chats 12345678 12121233` \n\n",
            reply_to_message_id=message.id
        )


def is_valid_chat_id(chat_id):
    try:
        int(chat_id)
        return True
    except ValueError:
        return False


async def file_size_formatter(file_size):
    if file_size < 1024:
        return f"{file_size} Bytes"
    elif 1024 <= file_size < 1048576:
        return f"{file_size / 1024:.2f} KB"
    elif 1048576 <= file_size < 1073741824:
        return f"{file_size / 1048576:.2f} MB"
    elif 1073741824 <= file_size:
        return f"{file_size / 1073741824:.2f} GB"


@bot.on_message(filters.command("get_chat_id"))
@check_owner
async def get_current_chat(client, message):
    # check if the user is the owner of the bot and to avoid spamming
    if client.me.id == message.from_user.id:
        current_chat = message.chat.id
        text = "╔════════ ≪ °❈° ≫ ════════\n"
        text += " • Chat ID: `%s`" % current_chat + "\n"
        text += " • Chat Type: %s" % message.chat.type + "\n"
        text += " • Chat Title/UserName: %s" % (message.chat.username if message.chat.username else message.chat.title)
        text += "\n╚════════ ≪ °❈° ≫ ════════"
        await bot.send_message(chat_id=message.chat.id, text=text)


# @bot.on_message(filters.command("cancel"))
async def update_my_progress(current, total, message=None, download_message=None, is_upload=False):
    percent = (current / total) * 100
    new_message = download_message.text.markdown + f"\nDownloading... {percent:.2f}%" if not is_upload \
        else f"Uploading... {percent:.2f}%"
    await bot.edit_message_text(chat_id=message.chat.id, message_id=download_message.id,
                                text=new_message,
                                )
    await asyncio.sleep(3.5)


@bot.on_message(filters=filters.video)
async def ghost_forward(client, message):
    if MY_CHAT:
        if str(message.chat.id) in MY_CHAT:
            if message.video:
                message_text = ("**Downloading...**\n**File Name:** `{}`\n**File Size:** `{}`\n**File ID:** `{}`\n\n"
                                "to Cancel this Download send `/cancel {}`").format(
                    message.video.file_name or "Not Available",
                    await file_size_formatter(
                        message.video.file_size),
                    message.video.file_id,
                    message.video.file_id)
                download_message = await bot.send_message(chat_id=message.chat.id, text=message_text,
                                                          reply_to_message_id=message.id)
                file_path = await message.download(block=True, progress=update_my_progress,
                                                   progress_args=(message, download_message, False))
                # Edit the message to indicate that the download is complete
                await bot.edit_message_text(chat_id=message.chat.id, message_id=download_message.id,
                                            text=f"Download complete! File will be uploaded to your saved message.")
                await bot.delete_messages(chat_id=message.chat.id, message_ids=download_message.id)
                await upload_file(client, message, file_path)
    else:
        await bot.send_message("me", "Oye You forgot about setting the chat_ids\nSend `/help` to Know more.")


# Implement your upload_file function and any other necessary functions


async def upload_file(client, message, file_path):
    # Generate the thumbnail
    thumbnail_path = file_path + ".jpg"
    width, height, duration = extract_screenshot(file_path)
    message_text = """**Uploading...**\n
                    **File Name:** `{}`\n
                    **File Size:** `{}`\n
                    **File ID:** `{}`\n
                    """.format(message.video.file_name, await file_size_formatter(message.video.file_size),
                               message.video.file_id)
    upload_message = await bot.send_message(chat_id=message.chat.id, text=message_text, reply_to_message_id=message.id)

    await bot.send_video(chat_id=group_id, video=file_path, caption=message.caption, progress=update_my_progress,
                         width=width,height=height,duration=duration,
                         progress_args=(message, upload_message),
                         thumb=thumbnail_path)
    await asyncio.sleep(5)
    os.remove(file_path)
    os.remove(thumbnail_path)
    await bot.delete_messages(chat_id=message.chat.id, message_ids=upload_message.id)


# run the app
bot.run()
