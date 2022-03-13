# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

# This module originally created by @spechide https://github.com/SpEcHiDe/UniBorg/blob/master/stdplugins/create_private_group.py

from telethon.tl import functions, types

from ..help import add_help_item
from userbot.events import register


@register(outgoing=True, pattern="^.create (b|g|c)(?: |$)(.*)")
async def telegraphs(grop):
    """ For .create command, Creating New Group & Channel """
    if not grop.text[0].isalpha() and grop.text[0] not in ("/", "#", "@", "!"):
        if grop.fwd_from:
            return
        type_of_group = grop.pattern_match.group(1)
        group_name = grop.pattern_match.group(2)
        if type_of_group == "b":
            try:
                result = await grop.client(functions.messages.CreateChatRequest(  # pylint:disable=E0602
                    users=["@MissRose_BOT"],
                    # Not enough users (to create a chat, for example)
                    # Telegram, no longer allows creating a chat with ourselves
                    title=group_name
                ))
                created_chat_id = result.chats[0].id
                await grop.client(functions.messages.DeleteChatUserRequest(
                    chat_id=created_chat_id,
                    user_id="@MissRose_BOT"
                ))
                result = await grop.client(functions.messages.ExportChatInviteRequest(
                    peer=created_chat_id,
                ))
                await grop.edit("Your `{}` Group Created Successfully. Join [{}]({})".format(group_name, group_name, result.link))
            except Exception as e:  # pylint:disable=C0103,W0703
                await grop.edit(str(e))
        elif type_of_group == "g" or type_of_group == "c":
            try:
                r = await grop.client(functions.channels.CreateChannelRequest(  # pylint:disable=E0602
                    title=group_name,
                    about="Welcome to this Channel",
                    megagroup=False if type_of_group == "c" else True
                ))
                created_chat_id = r.chats[0].id
                result = await grop.client(functions.messages.ExportChatInviteRequest(
                    peer=created_chat_id,
                ))
                await grop.edit("Your `{}` Group/Channel Created Successfully. Join [{}]({})".format(group_name, group_name, result.link))
            except Exception as e:  # pylint:disable=C0103,W0703
                await grop.edit(str(e))


add_help_item(
    "create",
    "Me",
    "Creating new group & channel",
    """
    `.create g`
    **Usage:** Create a private Group.

    `.create b`
    *"Usage:** Create a group with Bot.

    `.create c`
    **Usage:** Create a channel.
    """
)
