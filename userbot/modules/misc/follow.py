# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import urllib.parse

import requests

from ..help import add_help_item
from userbot.events import register
from userbot.utils import parse_arguments, extract_urls


@register(outgoing=True, pattern=r"^\.f(?:ollow)?(\s+[\S\s]+|$)")
async def follow_url(event):
    reply_message = await event.get_reply_message()
    message_text = event.pattern_match.group(1) or ""
    opts, message_text = parse_arguments(message_text, ['full'])

    await event.edit("Fetching links...")

    urls = []
    if message_text:
        urls.extend(extract_urls(message_text))
    elif reply_message:
        urls.extend(extract_urls(reply_message.text))
    else:
        await event.edit("No URLs found :(")
        return

    base_domain = not opts.get('full', False)
    await event.edit("Following links...")

    follows = []
    for url in urls:
        followed = await resolve_url(url, base_domain)
        follows.append((url, followed))

    message = []
    for follow in follows:
        message.append(f"**Original URL:** {follow[0]} \n**Followed URL:** {follow[1]}")

    message = '\n \n'.join(message)
    await event.edit(message, link_preview=False)


async def resolve_url(url: str, base_domain: bool = True) -> str:
    """Follow all redirects and return the base domain
    Args:
        url: The url
    Returns:
        The base comain as given by urllib.parse
        :param url: the url to resolve
        :param base_domain: if True only returns the host
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    if not url.startswith('http'):
        url = f'http://{url}'
    try:
        req = requests.get(url, headers=headers, timeout=3)
        url = req.url
    except ConnectionError:
        pass
    netloc = urllib.parse.urlparse(url).netloc
    # split up the result to only get the base domain
    # www.sitischu.com => sitischu.com
    _base_domain = netloc.split('.', maxsplit=netloc.count('.') - 1)[-1]
    if _base_domain and base_domain:
        url = _base_domain
    return url


add_help_item(
    "followlink",
    "Misc",
    "Follow a link or any number of links to their "
    "destination. Mainly for use with short URLs.",
    """
    `.f(ollow) (link1) (link2) ... (linkN)`
    
    Or, in reply to a message containing links
    `.f(ollow)`
    """
)
