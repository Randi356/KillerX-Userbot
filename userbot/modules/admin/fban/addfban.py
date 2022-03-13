# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

from userbot import is_mongo_alive
from userbot.events import register
from userbot.modules.admin.fban.fban_db import add_chat_fban


@register(outgoing=True, pattern=r"^\.addfban")
async def add_to_fban(chat):
    if not is_mongo_alive():
        await chat.edit("`Database connections failing!`")
        return
    await add_chat_fban(chat.chat_id)
    await chat.edit("`Added this chat under the Fbanlist!`")
