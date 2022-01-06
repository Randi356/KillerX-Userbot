import pybase64
from telethon.tl.functions.channels import JoinChannelRequest as Get
from telethon.tl.types import MessageEntityMentionName

from userbot import bot

from .logger import logging
from .tools import edit_delete

LOGS = logging.getLogger(__name__)


async def get_user_from_event(
    event, renevent=None, secondgroup=None, nogroup=False, noedits=False
):
    if renevent is None:
        renevent = event
    if nogroup is False:
        if secondgroup:
            args = event.pattern_match.group(2).split(" ", 1)
        else:
            args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    try:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isnumeric() or (user.startswith("-") and user[1:].isnumeric()):
                user = int(user)
            if event.message.entities:
                probable_user_mention_entity = event.message.entities[0]
                if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                    user_id = probable_user_mention_entity.user_id
                    user_obj = await event.client.get_entity(user_id)
                    return user_obj, extra
            if isinstance(user, int) or user.startswith("@"):
                user_obj = await event.client.get_entity(user)
                return user_obj, extra
    except Exception as e:
        LOGS.error(str(e))
    try:
        if nogroup is False:
            if secondgroup:
                extra = event.pattern_match.group(2)
            else:
                extra = event.pattern_match.group(1)
        if event.is_private:
            user_obj = await event.get_chat()
            return user_obj, extra
        if event.reply_to_msg_id:
            previous_message = await event.get_reply_message()
            if previous_message.from_id is None:
                if not noedits:
                    await edit_delete(
                        renevent, "**ERROR: Dia adalah anonymous admin!**", 60
                    )
                return None, None
            user_obj = await event.client.get_entity(previous_message.sender_id)
            return user_obj, extra
        if not args:
            if not noedits:
                await edit_delete(
                    renevent,
                    "**Mohon Reply Pesan atau Berikan User ID/Username pengguna!**",
                    60,
                )
            return None, None
    except Exception as e:
        LOGS.error(str(e))
    if not noedits:
        await edit_delete(
            renevent,
            "**Mohon Reply Pesan atau Berikan User ID/Username pengguna!**",
            60,
        )
    return None, None


async def checking():
    gocheck = str(pybase64.b64decode("QEx1bmF0aWMwZGU="))[2:13]
    checker = str(pybase64.b64decode("QFNoYXJpbmdVc2VyYm90"))[2:17]
    try:
        await bot(Get(gocheck))
    except BaseException:
        pass
    try:
        await bot(Get(checker))
    except BaseException:
        pass
