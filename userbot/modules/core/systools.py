# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about the server. """

from asyncio import create_subprocess_shell as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from platform import python_version, uname
from shutil import which
from os import remove
from telethon import version

from ..help import add_help_item
from userbot import ALIVE_NAME, VERSION
from userbot.events import register
from userbot.modules import ALL_MODULES

# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
# ============================================


@register(outgoing=True, pattern="^\.sysd$")
async def sysdetails(sysd):
    """ For .sysd command, get system info using neofetch. """
    try:
        neo = "neofetch --stdout"
        fetch = await asyncrunapp(
            neo,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )

        stdout, stderr = await fetch.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        await sysd.edit("`" + result + "`")
    except FileNotFoundError:
        await sysd.edit("`Install neofetch first !!`")


@register(outgoing=True, pattern="^\.botver$")
async def bot_ver(event):
    """ For .botver command, get the bot version. """
    if which("git") is not None:
        invokever = "git describe --all --long"
        ver = await asyncrunapp(
            invokever,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await ver.communicate()
        verout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        invokerev = "git rev-list --all --count"
        rev = await asyncrunapp(
            invokerev,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await rev.communicate()
        revout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        await event.edit("`Userbot Version: "
                         f"{verout}"
                         "` \n"
                         "`Revision: "
                         f"{revout}"
                         "`")
    else:
        await event.edit(
            "Shame that you don't have git, You're running 5.0 - 'Extended' anyway"
        )


@register(outgoing=True, pattern="^\.pip(?: |$)(.*)")
async def pipcheck(pip):
    """ For .pip command, do a pip search. """
    pipmodule = pip.pattern_match.group(1)
    if pipmodule:
        await pip.edit("`Searching . . .`")
        invokepip = f"pip3 search {pipmodule}"
        pipc = await asyncrunapp(
            invokepip,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )

        stdout, stderr = await pipc.communicate()
        pipout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        if pipout:
            if len(pipout) > 4096:
                await pip.edit("`Output too large, sending as file`")
                file = open("output.txt", "w+")
                file.write(pipout)
                file.close()
                await pip.client.send_file(
                    pip.chat_id,
                    "output.txt",
                    reply_to=pip.id,
                )
                remove("output.txt")
                return
            await pip.edit("**Query: **\n`"
                           f"{invokepip}"
                           "`\n**Result: **\n`"
                           f"{pipout}"
                           "`")
        else:
            await pip.edit("**Query: **\n`"
                           f"{invokepip}"
                           "`\n**Result: **\n`No Result Returned/False`")
    else:
        await pip.edit("`Use .help pip to see an example`")


@register(outgoing=True, pattern="^\.alive$")
async def amireallyalive(alive):
    """ For .alive command, check if the bot is running.  """
    await alive.edit(
                     "**UBotX is alive!**\n\n"
                     f"**Telethon version:** `{version.__version__}` \n"
                     f"**Python version:** `{python_version()}` \n"
                     f"**UBotX version:** `{VERSION}` \n"
                     f"**Source:** [HERE](https://github.com/HitaloKun/TG-UBotX) \n\n"
                     f"**Modules loaded:** `{len(ALL_MODULES)}` \n"
                     f"**User:** `{DEFAULTUSER}`"
                     )


@register(outgoing=True, pattern="^\.aliveu")
async def amireallyaliveuser(username):
    """ For .aliveu command, change the username in the .alive command. """
    message = username.text
    output = '.aliveu [new user without brackets] nor can it be empty'
    if not (message == '.aliveu' or message[7:8] != ' '):
        newuser = message[8:]
        global DEFAULTUSER
        DEFAULTUSER = newuser
        output = 'Successfully changed user to ' + newuser + '!'
    await username.edit("`" f"{output}" "`")


@register(outgoing=True, pattern="^\.resetalive$")
async def amireallyalivereset(ureset):
    """ For .resetalive command, reset the username in the .alive command. """
    global DEFAULTUSER
    DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
    await ureset.edit("`" "Successfully reset user for alive!" "`")


add_help_item(
    "systools",
    "Core",
    "Some useful system tools",
    """
    `.alive`
    **Usage:** Type .alive to see wether your bot is working or not.

    `.aliveu` <text>
    **Usage:** Changes the 'user' in alive to the text you want.

    `.resetalive`
    **Usage:** Resets the user to default.

    `.botver`
    **Usage:** Shows the userbot version.

    `.pip` <module(s)>
    **Usage:** Does a search of pip modules(s).

    `.sysd`
    **Usage:** Shows system information using neofetch.
    """
)
