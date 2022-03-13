# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" UserBot module to clean the current chat of deleted accounts """

import asyncio
from datetime import datetime
from typing import Optional

from telethon.errors import UserAdminInvalidError, FloodWaitError
from telethon.events import NewMessage
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import Channel, Message, ChatBannedRights, User

from ..help import add_help_item
from userbot.utils import parse_arguments
from userbot.events import register
from userbot.utils.tgdoc import *


@register(outgoing=True, groups_only=True, pattern=r"^\.cleanup(\s+[\S\s]+|$)")
async def cleanup(e: NewMessage.Event) -> None:
    """Command to remove Deleted Accounts from a group or network."""
    params = e.pattern_match.group(1) or ""
    chat: Channel = await e.get_chat()
    keyword_args, _ = parse_arguments(params, ['limit', 'silent'])

    count_only = keyword_args.get('count', False)
    silent = keyword_args.get('silent', False)

    if not chat.creator and not chat.admin_rights:
        count_only = True
    waiting_message = None
    if silent:
        await e.message.delete()
    else:
        waiting_message = await e.edit('**Starting cleanup. This might take a while.**')
    response = await _cleanup_chat(e, count=count_only, progress_message=e.message)
    if not silent:
        await e.edit(str(response))
    if waiting_message:
        await waiting_message.delete()


async def _cleanup_chat(event, count: bool = False,
                        progress_message: Optional[Message] = None) -> TGDoc:
    chat: Channel = await event.get_chat()
    client = event.client
    user: User
    deleted_users = 0
    deleted_admins = 0
    user_counter = 0
    deleted_accounts_label = Bold('Removed Deleted Accounts')
    participant_count = (await client.get_participants(chat, limit=0)).total
    # the number will be 0 if the group has less than 25 participants
    modulus = (participant_count // 25) or 1
    async for user in client.iter_participants(chat):
        if progress_message is not None and user_counter % modulus == 0:
            progress = Section(Bold('Cleanup'),
                               KeyValueItem(Bold('Progress'),
                                            f'{user_counter}/{participant_count}'),
                               KeyValueItem(deleted_accounts_label, deleted_users))
            await progress_message.edit(str(progress))
        user_counter += 1
        if user.deleted:
            deleted_users += 1
            if not count:
                try:
                    await client(EditBannedRequest(
                        chat, user, ChatBannedRights(
                            until_date=datetime(2038, 1, 1),
                            view_messages=True
                        )
                    ))
                except UserAdminInvalidError:
                    deleted_admins += 1
                except FloodWaitError as error:
                    if progress_message is not None:
                        progress = Section(Bold('Cleanup | FloodWait'),
                                           Bold(f'Got FloodWait for {error.seconds}s. Sleeping.'),
                                           KeyValueItem(Bold('Progress'),
                                                        f'{user_counter}/{participant_count}'),
                                           KeyValueItem(deleted_accounts_label, deleted_users))
                        await progress_message.edit(str(progress))

                    await asyncio.sleep(error.seconds)
                    await client(EditBannedRequest(
                        chat, user, ChatBannedRights(
                            until_date=datetime(2038, 1, 1),
                            view_messages=True
                        )
                    ))

    return TGDoc(
        Section(Bold('Cleanup'),
                KeyValueItem(deleted_accounts_label, deleted_users),
                KeyValueItem(Bold('Deleted Admins'), deleted_admins) if deleted_admins else None))


add_help_item(
    "cleanup",
    "Admin",
    "Clean the current chat of deleted accounts",
    """
    .clean
    """
)
