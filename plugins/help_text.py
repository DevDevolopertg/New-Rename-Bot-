import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
import random
import time
import os
import sqlite3
import asyncio

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import script

import pyrogram

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from pyrogram.errors import UserNotParticipant

from plugins.rename_file import rename_doc


@Client.on_message(filters.command(["help"]))
def help_user(bot, update):
    bot.send_message(
        chat_id=update.chat.id,
        text=script.HELP_USER,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="📌 Contact 📌", url="https://t.me/Amal_PM")]]),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_to_message_id=update.id
    )


@Client.on_message(filters.command(["start"]))
def send_start(bot, update):
    # logger.info(update)
    
    bot.send_message(
        chat_id=update.chat.id,
        text=script.START_TEXT.format(update.from_user.first_name),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_to_message_id=update.id
    )


@Client.on_message(filters.command(["upgrade"]))
def upgrade(bot, update):
    # logger.info(update)

    bot.send_message(
        chat_id=update.chat.id,
        text=script.UPGRADE_TEXT,
        parse_mode=enums.ParseMode.HTML,
        reply_to_message_id=update.id,
        disable_web_page_preview=True
    )

    
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.voice | filters.video_note))
async def rename_cb(bot, update):
    stickers = [
        "CAACAgUAAx0CR52brgABAztWYMr0c6pnuuyax0lMJa6fMTHVb90AAp4CAALt_CBW_K1bvpTAQg0eBA",
        "CAACAgUAAx0CR52brgABAztyYMr0_i-Da3NCXbEAAWpUiSbaXdFBAAJRAgAClhhxVFl1D3zKX_HDHgQ",
        "CAACAgUAAx0CR52brgABAzt2YMr1ZhaD1QqaLAt-in6TH535YEkAAiQCAAKtkLBVLS6YjJCDJoYeBA",
        "CAACAgUAAx0CR52brgABAzt5YMr1zf9AZcfWXHpcmw5nG8deom0AAsoAA5xr3DzY2D0P8fUfaB4E",
        "CAACAgUAAx0CR52brgABAzt-YMr2CYT4V992bKUT6GpAYZumPCoAAvgAA5xr3Dz7JrHmMtOI3R4E",
        "CAACAgUAAx0CR52brgABAzuBYMr2R1aHvk9genINSQlwYt9xSZUAAscAA4avgRoka_uuHm3rzR4E",
        "CAACAgUAAx0CR52brgABAzuHYMr2fowuk7J0jbqv1UeFmnTT6ygAAjoAA2nyaCZ7Tqu2UnozDh4E"
    ]
    
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.send_sticker(
            chat_id=update.chat.id,
            sticker=random.choice(stickers)
        )
        return
 
    file = update.document or update.video or update.audio or update.voice or update.video_note
    try:
        filename = file.file_name
    except:
        filename = "Not Available"
    
    await bot.send_message(
        chat_id=update.chat.id,
        text="<b>File Name</b> : <code>{}</code> \n\n <b> Select the desired option below 😇</b>".format(filename),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="📂 Rename 📂", callback_data="rename_button")],
                                                [InlineKeyboardButton(text="❌ Cancel ❌", callback_data="cancel_e")]]),
        parse_mode=enums.ParseMode.HTML,
        reply_to_message_id=update.id,
        disable_web_page_preview=True   
    )   


async def cancel_extract(bot, update):
    
    await bot.send_message(
        chat_id=update.chat.id,
        text="<b>Process Cancelled 🙃</b>",
    )
