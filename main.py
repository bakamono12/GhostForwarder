import time
import os
import generate_thumb
import random
from pyrogram import Client, filters

# session string from auth.py
session_string = os.environ.get("SESSION_STRING", None)

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


@bot.on_message(filters.command("boomer"))
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


@bot.on_message(filters.command("get_chat_id"))
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


@bot.on_message(filters=filters.video)
async def ghost_forward(client, message):
    if MY_CHAT:
        if str(message.chat.id) in MY_CHAT:
            if message.video:
                download_message = await bot.send_message(chat_id=message.chat.id, text="Downloading... 0%")

                async def update_progress(current, total):
                    percent = (current / total) * 100
                    await bot.edit_message_text(chat_id=message.chat.id, message_id=download_message.id,
                                                text=f"Downloading... {percent:.2f}%")
                    time.sleep(3.5)

                file_path = await message.download(block=True, progress=update_progress)

                # Edit the message to indicate that the download is complete
                await bot.edit_message_text(chat_id=message.chat.id, message_id=download_message.id,
                                            text=f"Download complete! File will be uploaded to your saved message.")

                await upload_file(client, message, file_path)
    else:
        await bot.send_message("me", "Oye You forgot about setting the chat_ids\nSend `/help` to Know more.")


async def upload_file(client, message, file_path):
    # Generate the thumbnail
    thumbnail_path = file_path + ".jpg"
    generate_thumb.generate_thumbnail(file_path, thumbnail_path)
    upload_message = await bot.send_message(chat_id=message.chat.id, text="Uploading... 0%")

    async def update_progress(current, total):
        percent = (current / total) * 100
        await bot.edit_message_text(chat_id=message.chat.id, message_id=upload_message.id,
                                    text=f"Uploading... {percent:.2f}%")
        time.sleep(3.5)

    await bot.send_video(chat_id="me", video=file_path, caption=message.caption, progress=update_progress,
                         thumb=thumbnail_path)
    time.sleep(5)
    os.remove(file_path)
    os.remove(thumbnail_path)


# run the app
bot.run()
