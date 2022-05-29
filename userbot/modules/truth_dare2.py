# from https://github.com/Randi356/VEGETA-USERBOT
# by Rendy
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import bot, CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.truth2(?: |$)(.*)")
async def _(event):
    await event.edit("Mengirim pesan truth...")
    async with bot.conversation("@truthordaresbot") as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=1206492140)
            )
            await conv.send_message("/truth")
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit("Harap unblock `@truthordaresbot` dan coba lagi")
            return
        await event.edit(f"**Pesan truth**\n\n{response.message.message}")


@register(outgoing=True, pattern=r"^\.dare2(?: |$)(.*)")
async def _(event):
    await event.edit("Mengirim pesan dare...")
    async with bot.conversation("@truthordaresbot") as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=1206492140)
            )
            await conv.send_message("/dare")
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit("Harap unblock `@truthordaresbot` dan coba lagi")
            return
        await event.edit(f"**Pesan dare**\n\n{response.message.message}")



CMD_HELP.update(
    {
        "truth_dare2": "** Plugin :** truth_dare2\
        \n\n  •  Perintah : `.truth2`\
        \n  •  Function : Untuk mengirim pesan truth\
        \n\n  •  Perintah : `.dare2`\
        \n  •  Function : Untuk mengirim pesan dare\
"
    }
)
