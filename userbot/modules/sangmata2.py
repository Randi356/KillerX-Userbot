# Credits @CuteInspire
# Made by Rendy
# Create file

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import bot, CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.sgu(?: |$)(.*)")
async def _(event):
    await event.edit("Prossing....")
    async with bot.conversation("@SangMataInfo_Bot") as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=461843263)
            )
            await conv.send_message("/check_username")
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit("Harap unblock `@SangMataInfo_Bot` dan coba lagi")
            return
        await event.reply(f"**Usernames**\n\n{response.message.message}")
