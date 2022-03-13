# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# Adapted module from https://github.com/nunopenim/tguserbot

from datetime import datetime
from os import path, remove
from pySmartDL import SmartDL
from urllib.error import HTTPError, URLError

from telethon.errors import ChatAdminRequiredError, ChatSendMediaForbiddenError
from telethon.errors.rpcerrorlist import MessageTooLongError
from telethon.tl.types import User

from ..help import add_help_item
from userbot import BOTLOG_CHATID, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register


@register(outgoing=True, pattern="^.cascheck ?(.*)")
async def cascheck(cas): #checks if a user, or all users in a group are cas banned
    if not cas.text[0].isalpha() and cas.text[0] in ("."):
        if cas.reply_to_msg_id:
            replied_msg = await cas.get_reply_message()
            chat = replied_msg.from_id
        else:
            chat = cas.pattern_match.group(1)
            if chat:
                try:
                    chat = int(chat)
                except ValueError:
                    pass
        if not chat:
            chat = cas.chat_id
        try:
            info = await cas.client.get_entity(chat)
        except (TypeError, ValueError) as err:
            await cas.edit(str(err))
            return
        exportcsv = TEMP_DOWNLOAD_DIRECTORY + "/export.csv"
        user_ids = []
        if path.exists(exportcsv):
            if isCSVoutdated():
                await cas.edit("`Auto updating CAS data...`")
                print("CASCHECK: Auto update CAS data started")
                await casupdater(cas, showinfo=False)
            await cas.edit("`Processing...`")
            with open(exportcsv) as data:
                for cas_id in data:
                    user_ids.append(int(cas_id))
        else:
            await cas.edit("`CAS data not found. Please use .casupdate command to get the latest CAS data`")
            return
        try:
            if type(info) is User:  # check an user only
                if info.id in user_ids:
                    if not info.deleted:
                        text = f"Warning! [{info.first_name}](tg://user?id={info.id}) [ID: `{info.id}`] is CAS Banned!"
                    else:
                        text = f"Warning! Deleted Account [ID: `{info.id}`] is CAS Banned!"
                else:
                    text = f"[{info.first_name}](tg://user?id={info.id}) is not CAS Banned"
            else:  # check for all members in a chat
                title = info.title if info.title else "this chat"
                cas_count, members_count = (0,)*2
                text_users = ""
                async for user in cas.client.iter_participants(info.id):
                    if user.id in user_ids:
                        cas_count += 1
                        if not user.deleted:
                            text_users += f"\n{cas_count}. [{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                        else:
                            text_users += f"\n{cas_count}. Deleted Account `{user.id}`"
                    members_count += 1
                text = "Warning! `{}` of `{}` users are CAS Banned in **{}**:\n".format(cas_count, members_count, title)
                text += text_users
                if not cas_count:
                    text = f"`No CAS Banned users found in {title}`"
        except ChatAdminRequiredError as carerr:
            await cas.edit("`CAS check failed: Admin privileges are required`")
            print("ChatAdminRequiredError:", carerr)
            return
        except BaseException as be:
            await cas.edit("`CAS check failed`")
            print("BaseException:", be)
            return
        finally:
            data.close()
        try:
            await cas.edit(text)
        except MessageTooLongError as mtle:
            print("MessageTooLongError:", mtle)
            await cas.edit("`Jesus christ, there are too many CAS Banned users in this chat. Uploading list as a file...`")
            temp_file = open("caslist.txt", "w+")
            temp_file.write(text)
            temp_file.close()
            try:
                await cas.client.send_file(cas.chat_id, "caslist.txt")
            except ChatSendMediaForbiddenError as f:
                await cas.edit("`Failed to upload list: send media isn't allowed in this chat.`")
                print("ChatSendMediaForbiddenError:", f)
            except BaseException as be:
                await cas.edit("`Failed to upload list`")
                print("BaseException:", be)
            remove("caslist.txt")
            return

def isCSVoutdated() -> bool: #checks if csv is a day or more old
    csv_file = TEMP_DOWNLOAD_DIRECTORY + "/export.csv"
    if not path.exists(csv_file):
        return False
    file_date = datetime.fromtimestamp(path.getmtime(csv_file))
    duration = datetime.today() - file_date
    if duration.days >= 1:
        return True
    else:
        return False

@register(outgoing=True, pattern="^.casupdate$")
async def casupdate(event): #updates cas csv
    if not event.text[0].isalpha() and event.text[0] in ("."):
        await casupdater(event, showinfo=True)
        return

async def casupdater(down, showinfo: bool): #csv downloader
    url = "https://combot.org/api/cas/export.csv"
    filename = TEMP_DOWNLOAD_DIRECTORY + "/export.csv"
    if showinfo:
        await down.edit("`Connecting...`")
    try:
        downloader = SmartDL(url, filename, progress_bar=False)
        downloader.start(blocking=False)
        if showinfo:
            await down.edit("`Downloading...`")
    except HTTPError as http:
        await down.edit("`Connection failed: internal server error occured`")
        print("HTTPError:", http)
        return
    except URLError as urle:
        await down.edit("`Connection failed: server not reachable`")
        print("URLError:", urle)
        return
    except IOError as io:
        await down.edit(f"`I/O Error: {io}`")
        print("IOError:", io)
        return
    except Exception as e:
        await down.edit(f"`Update failed: {be}`")
        print("Exception:", e)
        return
    if downloader.isSuccessful():
        if showinfo:
            await down.edit("`Successfully updated latest CAS CSV data`")
        print("CASUPATE download speed: %s" % downloader.get_speed(human=True))
        print("CASUPATE status: %s" % downloader.get_status())
        print("CASUPATE download time: %s seconds" % round(downloader.get_dl_time(), 2))
    else:
        await down.edit("`Update failed`")
        for error in downloader.get_errors():
            print(str(error))
    return


add_help_item(
    "cas",
    "Admin",
    "Combo Anti-Spam System (CAS)",
    """
    `.cascheck` [optional <reply/user id/username/chat id/invite link>]
    **Usage:** Allows you to check an user, channel (with admin flag) or a whole group for CAS Banned users.

    `.casupdate`
    **Usage:** Get the latest CAS CSV list from combot.org. Required for .cascheck.
    """
)
