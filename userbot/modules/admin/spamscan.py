# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

from telethon.tl.functions.users import GetFullUserRequest

from ..help import add_help_item
from userbot.events import register
from userbot.modules.admin.spamscore import score_user
from userbot.utils import make_mention
from userbot.utils.tgdoc import Section, Bold, KeyValueItem, String

SCANNING_MESSAGE = "**Scanning for potential spammers.** {}"


@register(outgoing=True, pattern=r"^\.s(?:pam)?b(?:lock)? scan$")
async def spamscan(e):
    users = []
    potentials = {}
    scanned = 0

    await e.edit(SCANNING_MESSAGE.format("**Collecting chat participants.**"))
    async for user in e.client.iter_participants(e.chat, aggressive=True):
        user_full = await e.client(GetFullUserRequest(user.id))
        users.append(user_full)

    total_users = len(users)
    await e.edit(SCANNING_MESSAGE.format(f"**Checking {total_users} users.**"))
    for user_full in users:
        score = await score_user(e, user_full)

        score_total = sum([i for i in score.values()])
        if score_total >= 5:
            potentials.update({user_full.user.id: score})

        scanned += 1
        if scanned % 5 == 0:
            await e.edit(SCANNING_MESSAGE.format(f"\n**Checked {scanned}/{total_users}. "
                                                 f"{total_users - scanned} remaining.**"))

    output = Section(Bold("Scan Results"))
    if potentials:
        for item in potentials.items():
            user_id, score = item
            user_full = await e.client(GetFullUserRequest(user_id))
            score_total = sum([i for i in score.values()])
            output.items.append(KeyValueItem(String(make_mention(user_full.user)),
                                             Bold(str(score_total))))
    else:
        output.items.append(String("No potential spammers found"))

    await e.edit(str(output))


add_help_item(
    "spamscan",
    "Admin",
    "Scan the current group for potential spammers "
    "using the spamscan algorithm.",
    """
    `.spamblock scan`

    Warning: this can take a __very__ long time.
    """
)
