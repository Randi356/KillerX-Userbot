# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import asyncio
from getpass import getuser
from os import remove

from ..help import add_help_item
from userbot import BOTLOG, BOTLOG_CHATID
from userbot.events import register


@register(outgoing=True, pattern=r"^\.term(?: |$)(.*)")
async def terminal_runner(term):
    """ For .term command, runs bash commands and scripts on your server. """
    from os import geteuid

    curruser = getuser()
    command = term.pattern_match.group(1)
    try:
        uid = geteuid()
    except ImportError:
        uid = "This ain't it chief!"

    if term.is_channel and not term.is_group:
        await term.edit("`Term commands aren't permitted on channels!`")
        return

    if not command:
        await term.edit("``` Give a command or use .help term for \
            an example.```")
        return

    if command in ("userbot.session", "config.env"):
        await term.edit("`That's a dangerous operation! Not Permitted!`")
        return

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) \
             + str(stderr.decode().strip())

    if len(result) > 4096:
        output = open("output.txt", "w+")
        output.write(result)
        output.close()
        await term.client.send_file(
            term.chat_id,
            "output.txt",
            reply_to=term.id,
            caption="`Output too large, sending as file`",
        )
        remove("output.txt")
        return

    if uid == 0:
        await term.edit("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await term.edit("`" f"{curruser}:~$ {command}" f"\n{result}" "`")

    if BOTLOG:
        await term.client.send_message(
            BOTLOG_CHATID,
            "#TERM\nTerminal Command " + command + " was executed sucessfully",
        )


add_help_item(
    "terminal",
    "Misc",
    "Execute a terminal command on the machine this "
    "bot is running on.",
    """
    `.term (command) [args]`
    """
)
