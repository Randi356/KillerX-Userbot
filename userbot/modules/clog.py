# Credits: cat userbot
# Ported by @vckyaz

import asyncio

from telethon import events

from userbot import BOTLOG_CHATID
from userbot import CMD_HELP, LOGS, bot
from userbot.modules.sql_helper import no_log_pms_sql
from userbot.modules.sql_helper.globals import addgvar, gvarstatus
from userbot.modules.ramcals import vcmention
from userbot.utils import _format
from telethon import events
from userbot.utils.tools import media_type

from userbot.events import register

class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0


LOG_CHATS_ = LOG_CHATS()


@bot.on(events.ChatAction)
async def logaddjoin(event):
    user = await event.get_user()
    chat = await event.get_chat()
    if not (user and user.is_self):
        return
    if hasattr(chat, "username") and chat.username:
        chat = f"[{chat.title}](https://t.me/{chat.username}/{event.action_message.id})"
    else:
        chat = f"[{chat.title}](https://t.me/c/{chat.id}/{event.action_message.id})"
    if event.user_added:
        tmp = event.added_by
        text = f"📩 **#ADD_LOG\n •** {vcmention(tmp)} **Menambahkan** {vcmention(user)}\n **• Ke Group** {chat}"
    elif event.user_joined:
        text = f"📨 **#JOIN_LOG\n •** [{user.first_name}](tg://user?id={user.id}) **Bergabung\n • Ke Group** {chat}"
    else:
        return
    await event.client.send_message(BOTLOG_CHATID, text)


@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
@bot.on(events.MessageEdited(incoming=True, func=lambda e: e.is_private))
async def monito_p_m_s(event):
    if BOTLOG_CHATID == -100:
        return
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") == "false":
        return
    sender = await event.get_sender()
    await asyncio.sleep(0.5)
    if not sender.bot:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id) and chat.id != 777000:
            if LOG_CHATS_.RECENT_USER != chat.id:
                LOG_CHATS_.RECENT_USER = chat.id
                if LOG_CHATS_.NEWPM:
                    await LOG_CHATS_.NEWPM.edit(
                        LOG_CHATS_.NEWPM.text.replace(
                            "**💌 #NEW_MESSAGE**",
                            f" • `{LOG_CHATS_.COUNT}` **Pesan**",
                        )
                    )
                    LOG_CHATS_.COUNT = 0
                LOG_CHATS_.NEWPM = await event.client.send_message(
                    BOTLOG_CHATID,
                    f"**💌 #MENERUSKAN #PESAN_BARU**\n** • Dari : **{_format.mentionuser(sender.first_name , sender.id)}\n** • User ID:** `{chat.id}`",
                )
            try:
                if event.message:
                    await event.client.forward_messages(
                        BOTLOG_CHATID, event.message, silent=True
                    )
                LOG_CHATS_.COUNT += 1
            except Exception as e:
                LOGS.warn(str(e))


@bot.on(events.NewMessage(incoming=True, func=lambda e: e.mentioned))
@bot.on(events.MessageEdited(incoming=True, func=lambda e: e.mentioned))
async def log_tagged_messages(event):
    if BOTLOG_CHATID == -100:
        return
    hmm = await event.get_chat()

    if gvarstatus("GRUPLOG") and gvarstatus("GRUPLOG") == "false":
        return
    if (
        (no_log_pms_sql.is_approved(hmm.id))
        or (BOTLOG_CHATID == -100)
        or (await event.get_sender() and (await event.get_sender()).bot)
    ):
        return
    full = None
    try:
        full = await event.client.get_entity(event.message.from_id)
    except Exception as e:
        LOGS.info(str(e))
    messaget = media_type(event)
    resalt = f"<b>📨 #TAGS #MESSAGE</b>\n<b> • Dari : </b>{_format.htmlmentionuser(full.first_name , full.id)}"
    if full is not None:
        resalt += f"\n<b> • Grup : </b><code>{hmm.title}</code>"
    if messaget is not None:
        resalt += f"\n<b> • Jenis Pesan : </b><code>{messaget}</code>"
    else:
        resalt += f"\n<b> • 👀 </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'>Lihat Pesan</a>"
    resalt += f"\n<b> • Message : </b>{event.message.message}"
    await asyncio.sleep(0.5)
    if not event.is_private:
        await event.client.send_message(
            BOTLOG_CHATID,
            resalt,
            parse_mode="html",
            link_preview=False,
        )


@register(pattern=r"^\.save(?: |$)(.*)")
async def log(log_text):
    if BOTLOG_CHATID:
        if log_text.reply_to_msg_id:
            reply_msg = await log_text.get_reply_message()
            await reply_msg.forward_to(BOTLOG_CHATID)
        elif log_text.pattern_match.group(1):
            user = f"**#LOG / Chat ID:** {log_text.chat_id}\n\n"
            textx = user + log_text.pattern_match.group(1)
            await log_text.client.send_message(BOTLOG_CHATID, textx)
        else:
            await log_text.edit("**Apa yang harus saya simpan?**")
            return
        await log_text.edit("**Berhasil disimpan di Grup Log**")
    else:
        await log_text.edit(
            "**Untuk Menggunakan Module ini, Anda Harus Mengatur** `BOTLOG_CHATID` **di Config Vars**")


@register(pattern=r"^\.log$")
async def set_no_log_p_m(event):
    if BOTLOG_CHATID != -100:
        chat = await event.get_chat()
        if no_log_pms_sql.is_approved(chat.id):
            no_log_pms_sql.disapprove(chat.id)
            await event.edit("**LOG Chat dari Grup ini Berhasil Diaktifkan**")


@register(pattern=r"^\.nolog$")
async def set_no_log_p_m(event):
    if BOTLOG_CHATID != -100:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id):
            no_log_pms_sql.approve(chat.id)
            await event.edit("**LOG Chat dari Grup ini Berhasil Dimatikan**")


@register(pattern=r"^\.pmlog (on|off)$")
async def set_pmlog(event):
    if BOTLOG_CHATID == -100:
        return await event.edit("**Untuk Menggunakan Module ini, Anda Harus Mengatur** `BOTLOG_CHATID` **di Config Vars**")
    input_str = event.pattern_match.group(1)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") == "false":
        PMLOG = False
    else:
        PMLOG = True
    if PMLOG:
        if h_type:
            await event.edit("**PM LOG Sudah Diaktifkan**")
        else:
            addgvar("PMLOG", h_type)
            await event.edit("**PM LOG Berhasil Dimatikan**")
    elif h_type:
        addgvar("PMLOG", h_type)
        await event.edit("**PM LOG Berhasil Diaktifkan**")
    else:
        await event.edit("**PM LOG Sudah Dimatikan**")


@register(pattern=r"^\.gruplog (on|off)$")
async def set_gruplog(event):
    if BOTLOG_CHATID == -100:
        return await event.edit("**Untuk Menggunakan Module ini, Anda Harus Mengatur** `BOTLOG_CHATID` **di Config Vars**")
    input_str = event.pattern_match.group(1)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    if gvarstatus("GRUPLOG") and gvarstatus("GRUPLOG") == "false":
        GRUPLOG = False
    else:
        GRUPLOG = True
    if GRUPLOG:
        if h_type:
            await event.edit("**Group Log Sudah Diaktifkan**")
        else:
            addgvar("GRUPLOG", h_type)
            await event.edit("**Group Log Berhasil Dimatikan**")
    elif h_type:
        addgvar("GRUPLOG", h_type)
        await event.edit("**Group Log Berhasil Diaktifkan**")
    else:
        await event.edit("**Group Log Sudah Dimatikan**")


CMD_HELP.update(
    {
        "log": f"**Modules : **`log`\
        \n\n •  **Command  :** `.save`\
        \n  •  **Function  : **__Untuk Menyimpan pesan yang ditandai ke grup pribadi.__\
        \n\n •  **Command  :** `.log`\
        \n  •  **Function  : **__Untuk mengaktifkan Log Chat dari obrolan/grup itu.__\
        \n\n •  **Command  :** `.nolog`\
        \n  •  **Function  : **__Untuk menonaktifkan Log Chat dari obrolan/grup itu.__\
        \n\n •  **Command  :** `.pmlog on/off`\
        \n  •  **Function  : **__Untuk mengaktifkan atau menonaktifkan pencatatan pesan pribadi__\
        \n\n •  **Command  :** `.gruplog on/off`\
        \n  •  **Function  : **__Untuk mengaktifkan atau menonaktifkan tag grup, yang akan masuk ke grup pmlogger.__"
    }
)
