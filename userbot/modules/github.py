import aiohttp
from userbot.events import register
from userbot import CMD_HELP


@register(pattern=r".git (.*)", outgoing=True)
async def github(event):
    URL = f"https://api.github.com/users/{event.pattern_match.group(1)}"
    await event.get_chat()
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as request:
            if request.status == 404:
                return await event.reply("`" + event.pattern_match.group(1) +
                                         " not found`")

            result = await request.json()

            url = result.get("html_url", None)
            name = result.get("name", None)
            company = result.get("company", None)
            bio = result.get("bio", None)
            created_at = result.get("created_at", "Not Found")

            REPLY = (
                f"GitHub Info for `{event.pattern_match.group(1)}`"
                f"\nUsername: `{name}`\nBio: `{bio}`\nURL: {url}"
                f"\nCompany: `{company}`\nCreated at: `{created_at}`"
            )

            if not result.get("repos_url", None):
                return await event.edit(REPLY)
            async with session.get(result.get("repos_url", None)) as request:
                result = request.json
                if request.status == 404:
                    return await event.edit(REPLY)

                result = await request.json()

                REPLY += "\nRepo:\n"

                for nr in range(len(result)):
                    REPLY += f"[{result[nr].get('name', None)}]({result[nr].get('html_url', None)})\n"

                await event.edit(REPLY)


CMD_HELP.update({
    "github": ".git <nama pengguna>"
    "\nPenjelasan: Seperti .whois tetapi untuk nama pengguna GitHub."
})
