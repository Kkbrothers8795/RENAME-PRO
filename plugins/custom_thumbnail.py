import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
import pyrogram

from config import Config

from translation import Translation
from pyrogram import filters
from pyrogram import Client

import database.database as sql
from PIL import Image
from database.database import *


@Client.on_message(filters.photo)
async def save_photo(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            msg_ids=update.msg_id,
            revoke=True
        )
        return

    if update.media_group_id is not None:
        # album is sent
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/" + str(update.media_group_id) + "/"
        # create download directory, if not exist
        if not os.path.isdir(download_location):
            os.makedirs(download_location)
        await sql.df_thumb(update.from_user.id, update.message_id)
        await bot.download_media(
            message=update,
            file_name=download_location
        )
    else:
        # received single photo
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
        await sql.df_thumb(update.from_user.id, update.message_id)
        await bot.download_media(
            message=update,
            file_name=download_location
        )
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.SAVED_CUSTOM_THUMB_NAIL,
            reply_to_msg_id=update.msg_id
        )


@Client.on_message(filters.command(["delthumb"]))
async def delete_thumbnail(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            msge_ids=update.msg_id,
            revoke=True
        )
        return

    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    #download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
    
    try:
        await sql.del_thumb(update.from_user.id) 
        #os.remove(download_location + ".json")
    except:
        pass
    try:
        os.remove(thumb_image_path)
    except:
        pass

    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DEL_ETED_CUSTOM_THUMB_NAIL,
        reply_to_msg_id=update.msg_id
    )


@Client.on_message(filters.command(["showthumb"]))
async def show_thumb(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            msg_ids=update.msg_id,
            revoke=True
        )
        return

    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    if not os.path.exists(thumb_image_path):
        mes = await thumb(update.from_user.id)
        if mes != None:
            m = await bot.get_messages(update.chat.id, mes.msg_id)
            await m.download(file_name=thumb_image_path)
            thumb_image_path = thumb_image_path
        else:
            thumb_image_path = None    
    
    if thumb_image_path is not None:
        try:
            await bot.send_photo(
                chat_id=update.chat.id,
                photo=thumb_image_path,
                reply_to_msg_id=update.msg_id
            )
        except:
            pass
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_THUMB_FOUND,
            reply_to_msg_id=update.msg_id
        )
