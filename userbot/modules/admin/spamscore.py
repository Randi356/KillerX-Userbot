# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import re
from io import BytesIO

from PIL import Image
from photohash import average_hash

from ..help import add_help_item
from userbot import spamwatch
from userbot.events import register
from userbot.utils import parse_arguments, get_user_from_event, make_mention

REDFLAG_WORDS = [
    'bitcoin', 'crypto', 'forex', 'invest',
    'sex', 'eth', 'model', 'xrp', 'btc'
]


@register(outgoing=True, pattern=r"^\.s(?:pam)?b(?:lock)? score(\s+[\S\s]+|$)")
async def spamscan_score(e):
    """ Test a single user against the spamscan algorithm """
    args, user = parse_arguments(e.pattern_match.group(1), ['forward'])

    args['forward'] = args.get('forward', True)
    args['user'] = user

    replied_user = await get_user_from_event(e, **args)
    if not replied_user:
        await e.edit("**Failed to get information for user**")
        return

    await e.edit(f"**Calculating spam score for** {make_mention(replied_user.user)}")

    score = await score_user(e, replied_user)
    score_total = sum([i for i in score.values()])

    output = f"**Spam score for** {make_mention(replied_user.user)}({replied_user.user.id}): **{score_total}**\n\n"

    if score_total > 0:
        output += "**Reasons:**\n"

    for reason in score.keys():
        output += f"{reason}\n"

    await e.edit(output)


async def score_user(event, userfull):
    """ Give a user a spam score based on several factors """
    user = userfull.user

    # Everyone starts with a score of 0. A lower score indicates
    # a lower chance of being a spammer. A higher score
    # indicates the opposite.
    score = {}

    hashes = await gather_profile_pic_hashes(event, user)
    total_hashes = len(hashes)
    matching_hashes = 0

    # User was flagged as a scammer
    if user.scam:
        score.update({'flagged as scammer': 5})

    # User is restricted
    if user.restricted:
        score.update({'restricted': 3})

    # No profile pic is a +2
    if total_hashes == 0:
        score.update({'no profile pic': 2})

    # A single profile pic can also be a red flag
    elif total_hashes == 1:
        score.update({'single profile pic': 2})

    # If all the profile pics are the same that's another red flag
    elif total_hashes >= 2 and len(set(hashes)) == 1:
        score.update({'profile pics same': 2})

    if matching_hashes > 0:
        # If there are matching hashes that's an automatic +5
        score.update({f'blacklisted photos ({total_hashes}/{matching_hashes})': 5})

    # Lots of spammers try and look normal by having a normal(ish)
    # first and last name. A first AND last name with no special
    # characters is a good indicator. This is a +1.
    if ((user.first_name and re.match(r"^[a-zA-Z0-9\s_]+$", user.first_name)) and
            (user.last_name and re.match(r"^[a-zA-Z0-9\s_]+$", user.last_name))):
        score.update({'alphanum first and last name': 1})

    if user.first_name and user.last_name:
        # Another thing spammers seem to have is very predictable names.
        # These come in many forms like one uppercase name and one
        # lowercase, all upper or lower, or having one name be
        # numeric. Either way they generally have a first
        # name and a last name.
        if user.first_name.isupper() and user.first_name.islower():
            score.update({'first upper last lower': 3})
        elif user.last_name.isupper() and user.last_name.islower():
            score.update({'first lower last upper': 3})
        elif user.first_name.islower() and user.last_name.islower():
            # This appears less bot like than all upper
            score.update({'lowercase name': 2})
        elif user.first_name.isupper() and user.last_name.isupper():
            score.update({'uppercase name': 3})
        elif user.first_name.isnumeric() or user.last_name.isnumeric():
            score.update({'numeric name': 2})

    # Another popular thing is bots with japanese, chinese, cyrillic,
    # and arabic names. A full match here is worth +3.
    if (user.first_name and is_cjk(user.first_name) or
            (user.last_name and is_cjk(user.last_name))):
        score.update({'ch/jp name': 3})
    elif (user.first_name and is_arabic(user.first_name) or
          (user.last_name and is_arabic(user.last_name))):
        score.update({'arabic name': 3})
    elif (user.first_name and is_cyrillic(user.first_name) or
          (user.last_name and is_cyrillic(user.last_name))):
        # Cyrillic names are more common, so we'll drop the score here.
        score.update({'cyrillic name': 2})

    if userfull.about and is_cjk(userfull.about):
        score.update({'ch/jp bio': 2})
    elif userfull.about and is_arabic(userfull.about):
        score.update({'arabic bio': 2})
    elif userfull.about and is_cyrillic(userfull.about):
        score.update({'cyrillic bio': 2})

    # A username ending in numbers is a +1
    if user.username:
        if re.match(r".*[0-9]+$", user.username):
            score.update(({'sequential username': 2}))
    else:
        score.update({'no username': 2})

    if userfull.about:
        # Check the bio for red flag words. Each one of these is a +3.
        total_red_flags = 0
        for word in REDFLAG_WORDS:
            if word in userfull.about.lower():
                total_red_flags += 1
        if total_red_flags > 0:
            score.update({f'red flag words x{total_red_flags}': total_red_flags * 3})

    # No bio is also an indicator worth an extra 2 points
    else:
        score.update({'no bio': 2})

    # Check if this person is banned in spamwatch. This is
    # basically a guarantee, and therefore nets a +5.
    if spamwatch:
        spamwatch_ban = spamwatch.get_ban(user.id)
        if spamwatch_ban:
            score.update({f'spamwatch ({spamwatch_ban.reason.lower()})': 5})

    return score


def is_cjk(string):
    return unicode_block_match(string, [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215),
                                        (63744, 64255), (65072, 65103), (65381, 65500),
                                        (131072, 196607)])


def is_arabic(string):
    return unicode_block_match(string, [(1536, 1791), (1792, 1871)])


def is_cyrillic(string):
    return unicode_block_match(string, [(1024, 1279)])


def unicode_block_match(string, block):
    re.sub(r"\s+", "", string)
    for char in string:
        if any([start <= ord(char) <= end for start, end in block]):
            return True
    return False


async def gather_profile_pic_hashes(event, user):
    hashes = []
    async for photo in event.client.iter_profile_photos(user):
        io = BytesIO()
        await event.client.download_media(photo, io)
        image = Image.open(io)
        hashes.append(average_hash(image))
    return hashes


add_help_item(
    "spamscore",
    "Admin",
    "Get the spam score of the selected user.",
    """
    `.spamblock score [options] (user id|username)`

    Or, in reply to a message
    `.spamblock score [options]`

    **Options:**
    `.forward`: Follow forwarded message
    """
)
