# from https://github.com/Randi356/VEGETA-USERBOT
# BY RENDY
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from userbot import bot, CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.spill2(?: |$)(.*)")
async def _(event):
    await event.edit("Mengirim pesan spill...")
    async with bot.conversation("@Sodgame_bot") as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=1174980064)
            )
            await conv.send_message("/spill")
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit("Harap unblock `@Sodgame_bot` dan coba lagi")
            return
        await event.edit(f"**Pesan spill**\n\n{response.message.message}")


CMD_HELP.update(
    {
        "spill2": "** Plugin :** spill2\
        \n\n  •  Perintah : `.spill`\
        \n  •  Function : Untuk Pertanyaan\
    "
    }
)
