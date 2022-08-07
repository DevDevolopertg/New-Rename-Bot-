import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
import time
import asyncio
import pyrogram

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import script

from pyrogram import Client, filters, enums, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from plugins.helpers import progress_for_pyrogram

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from PIL import Image
from database.database import *


async def force_name(bot, message):

    await bot.send_message(
        message.reply_to_message.from_user.id,
        "Enter new name for media\n\nNote : Extension not required",
        reply_to_message_id=message.reply_to_message.id,
        reply_markup=ForceReply(True)
    )


@Client.on_message(filters.private & filters.reply & filters.text)
async def cus_name(bot, message):
    
    if (message.reply_to_message.reply_markup) and isinstance(message.reply_to_message.reply_markup, ForceReply):
        asyncio.create_task(rename_doc(bot, message))     
    else:
        print('No media present')

    
async def rename_doc(bot: Client, message: types.Message):
    
    mssg = await bot.get_messages(
        message.chat.id,
        message.reply_to_message.id
    )    
    
    media = mssg.reply_to_message

    
    if media.empty:
        await message.reply_text('Why did you delete that 😕', True)
        return
        
    filetype = media.document or media.video or media.audio or media.voice or media.video_note
    try:
        actualname = filetype.file_name
        splitit = actualname.split(".")
        extension = (splitit[-1])
    except:
        extension = "mkv"
    
    file_size = filetype.file_size


    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=message.reply_to_message.id,
        revoke=True
    )
    
    if message.from_user.id in Config.AUTH_USERS:
        file_name = message.text
        description = script.CUSTOM_CAPTION_UL_FILE.format(newname=file_name)
        download_location = Config.DOWNLOAD_LOCATION + "/"

        sendmsg = await bot.send_message(
            chat_id=message.chat.id,
            text=script.DOWNLOAD_START,
            reply_to_message_id=message.id
        )
        
        c_time = time.time()
        frwded = await media.forward(Config.LOG_CHANNEL)
        media = await bot.USER.get_messages(Config.LOG_CHANNEL, frwded.id)
        the_real_download_location = await bot.USER.download_media(
            message=media,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                script.DOWNLOAD_START,
                sendmsg,
                c_time
            )
        )
        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=script.SAVED_RECVD_DOC_FILE,
                    chat_id=message.chat.id,
                    message_id=sendmsg.id
                )
            except:
                await sendmsg.delete()
                sendmsg = await message.reply_text(script.SAVED_RECVD_DOC_FILE, quote=True)

            new_file_name = download_location + file_name + "." + extension
            os.rename(the_real_download_location, new_file_name)
            try:
                await bot.edit_message_text(
                    text=script.UPLOAD_START,
                    chat_id=message.chat.id,
                    message_id=sendmsg.id
                    )
            except:
                await sendmsg.delete()
                sendmsg = await message.reply_text(script.UPLOAD_START, quote=True)
            # logger.info(the_real_download_location)

            thumb_image_path = download_location + str(message.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                mes = await thumb(message.from_user.id)
                if mes != None:
                    m = await bot.get_messages(message.chat.id, mes.msg_id)
                    await m.download(file_name=thumb_image_path)
                    thumb_image_path = thumb_image_path
                else:
                    thumb_image_path = None                    
            else:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")

            c_time = time.time()
            """if file_size > 2000 * 1024 * 1024:
                client = bot.USER
                chat_id = Config.LOG_CHANNEL
            else:
                client = bot
                chat_id = message.chat.id"""
            client = bot.USER
            chat_id = Config.LOG_CHANNEL
            renamed_file = await bot.USER.send_document(
                chat_id=chat_id,
                document=new_file_name,
                thumb=thumb_image_path,
                parse_mode=enums.ParseMode.MARKDOWN,
                caption=script.CAPTION.format(file_name),
                # reply_markup=reply_markup,
                progress=progress_for_pyrogram,
                progress_args=(
                    script.UPLOAD_START,
                    sendmsg, 
                    c_time
                )
            )
            #if renamed_file.chat.id == Config.LOG_CHANNEL:
            await bot.copy_message(message.chat.id, Config.LOG_CHANNEL, renamed_file.id)

            try:
                os.remove(new_file_name)
            except:
                pass                 
            try:
                os.remove(thumb_image_path)
            except:
                pass  
            try:
                await bot.edit_message_text(
                    text=script.AFTER_SUCCESSFUL_UPLOAD_MSG,
                    chat_id=message.chat.id,
                    message_id=sendmsg.id,
                    disable_web_page_preview=True
                )
            except:
                await sendmsg.delete()
                await message.reply_text(script.AFTER_SUCCESSFUL_UPLOAD_MSG, quote=True)
                
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="You're not Authorized to do that!",
            reply_to_message_id=message.id
        )
