# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import requests

from ..help import add_help_item
from userbot.events import register
from userbot.utils import parse_arguments


@register(outgoing=True, pattern=r"^\.docs\s+(.*)")
async def doc_search(e):
    params = e.pattern_match.group(1)
    args, lib = parse_arguments(params, ['version'])
    lib = lib.strip()

    version = int(args.get('version', 3))
    python_url = f"https://docs.python.org/{version}/library/{lib}.html"
    pip_url = f"https://pypi.org/project/{lib}/"

    await e.edit(f"Searching docs for `{lib}`...")
    if requests.get(python_url).status_code == 200:
        response = f"[Python {version} documentation for {lib}]({python_url})"
        await e.edit(response)
    elif requests.get(pip_url).status_code == 200:
        readthedocs_url = f"https://readthedocs.org/projects/{lib}/"
        if requests.get(readthedocs_url).status_code == 200:
            response = f"[Documentation for {lib} on Read the Docs]({readthedocs_url})"
            await e.edit(response)
    else:
        await e.edit(f"No docs found for `{lib}`...")

add_help_item(
    "docs",
    "Misc",
    "Searches doc sources (currently python.org and "
    "readthedocs.org) for module documentation.",
    """
    `.docs (module)`
    """
)