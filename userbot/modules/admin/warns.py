# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# Ported from SpEcHiDe UniBorg by github.com/HitaloKun/TG-UBotX

import html

from ..help import add_help_item
from userbot.events import register
import userbot.modules.sql_helper.warns_sql as sql


@register(outgoing=True, pattern=r"^\.warn (.*)")
async def _(event):
    if event.fwd_from:
        return
    warn_reason = event.pattern_match.group(1)
    reply_message = await event.get_reply_message()
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    num_warns, reasons = sql.warn_user(reply_message.from_id, event.chat_id, warn_reason)
    if num_warns >= limit:
        sql.reset_warns(reply_message.from_id, event.chat_id)
        if soft_warn:
            logger.info("TODO: kick user")
            reply = "<code>{}</code> warnings, <u><a href='tg://user?id={}'>user</a></u> has been kicked!".format(limit, reply_message.from_id)
        else:
            logger.info("TODO: ban user")
            reply = "<code>{}</code> warnings, <u><a href='tg://user?id={}'>user</a></u> has been banned!".format(limit, reply_message.from_id)
    else:
        reply = "<u><a href='tg://user?id={}'>User</a></u> has <code>{}/{}</code> warnings... watch out!".format(reply_message.from_id, num_warns, limit)
        if warn_reason:
            reply += "\nReason for last warn:\n<code>{}</code>".format(html.escape(warn_reason))
    #
    await event.edit(reply, parse_mode="html")


@register(outgoing=True, pattern="^\.warns$")
async def _(event):
    if event.fwd_from:
        return
    reply_message = await event.get_reply_message()
    result = sql.get_warns(reply_message.from_id, event.chat_id)
    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(event.chat_id)
        if reasons:
            text = "This user has `{}/{}` warnings, for the following reasons:".format(num_warns, limit)
            text += "\n"
            text += reasons
            await event.edit(text)
        else:
            await event.edit("This user has `{}/{}` warning, but no reasons for any of them.".format(num_warns, limit))
    else:
        await event.edit("This user hasn't got any warnings!")


@register(outgoing=True, pattern="^\.resetwarns$")
async def _(event):
    if event.fwd_from:
        return
    reply_message = await event.get_reply_message()
    sql.reset_warns(reply_message.from_id, event.chat_id)
    await event.edit("Warnings have been reset!")


add_help_item(
    "warns",
    "Admin",
    "Userbot module containing commands for warn users",
    """
    `.warn`
    **Usage:** Warn a user.

    `.warns`
    **Usage:** See all warns for a user.

    `.resetwarns`
    **Usage:** Reset all warns of a user.
    """
)
