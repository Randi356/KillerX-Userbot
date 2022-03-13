# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

from github import InputFileContent

from ..help import add_help_item
from userbot import github
from userbot.events import register


@register(outgoing=True, pattern=r"^\.gist\s+([\S]+)\s+([\S\s]+)")
async def create_gist(e):
    if not github:
        await e.edit("Github information has not been set up", delete_in=3)
        return

    filename = e.pattern_match.group(1)
    match = e.pattern_match.group(2)
    reply_message = await e.get_reply_message()

    if match:
        message = match.strip()
    elif reply_message:
        message = reply_message.message.strip()
    else:
        await e.edit("There's nothing to paste.")
        return

    await e.edit("`Sending paste to Github...`")

    user = github.get_user()
    file = InputFileContent(message)
    gist = user.create_gist(True, {filename: file})

    await e.edit(f"Gist created. You can find it here {gist.html_url}.")

add_help_item(
    "gist",
    "Misc",
    "Create a gist using the supplied content or the "
    "replied to message.",
    """
    `.gist (content)`
    
    Or, in reply to a message
    `.gist`
    """
)