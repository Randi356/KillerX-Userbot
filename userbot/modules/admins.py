# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.

from asyncio import sleep
from os import remove

from telethon.errors import (
    BadRequestError,
    ChatAdminRequiredError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
    UserAdminInvalidError,
)
from telethon.errors.rpcerrorlist import MessageTooLongError, UserIdInvalidError
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    ChatAdminRights,
    ChatBannedRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
    PeerChat,
)

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, DEVS
from userbot import CMD_HANDLER as cmd
from userbot.events import register
from userbot.utils import (
    _format,
    edit_delete,
    edit_or_reply,
    ren_man,
    ren_handler,
)

# =================== CONSTANT ===================
PP_TOO_SMOL = "`Gambar Terlalu Kecil`"
PP_ERROR = "`Gagal Memproses Gambar`"
NO_ADMIN = "`Maaf Anda Bukan Admin:)`"
NO_PERM = "`Maaf Anda Tidak Mempunyai Izin!`"
NO_SQL = "`Berjalan Pada Mode Non-SQL`"

CHAT_PP_CHANGED = "`Berhasil Mengubah Profil Gru anjing`"
CHAT_PP_ERROR = (
    "`Ada Masalah Dengan Memperbarui Foto,`"
    "`Mungkin Karna Anda Bukan Admin,`"
    "`Atau Tidak Mempunyai Izin.`"
)
INVALID_MEDIA = "`Media Tidak Valid`"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
# ================================================


@ren_cmd(pattern="setgpic( -s| -d)$")
async def set_group_photo(event):
    "For changing Group dp"
    flag = (event.pattern_match.group(1)).strip()
    if flag == "-s":
        replymsg = await event.get_reply_message()
        photo = None
        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await event.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split("/"):
                photo = await event.client.download_file(replymsg.media.document)
            else:
                return await edit_delete(event, INVALID_MEDIA)
        if photo:
            try:
                await event.client(
                    EditPhotoRequest(
                        event.chat_id, await event.client.upload_file(photo)
                    )
                )
                await edit_delete(event, CHAT_PP_CHANGED)
            except PhotoCropSizeSmallError:
                return await edit_delete(event, PP_TOO_SMOL)
            except ImageProcessFailedError:
                return await edit_delete(event, PP_ERROR)
            except Exception as e:
                return await edit_delete(event, f"**ERROR : **`{str(e)}`")
    else:
        try:
            await event.client(EditPhotoRequest(event.chat_id, InputChatPhotoEmpty()))
        except Exception as e:
            return await edit_delete(event, f"**ERROR : **`{e}`")
        await edit_delete(event, "**Foto Profil Grup Berhasil dihapus.**", 30)

@ren_cmd(outgoing=True, pattern=r"^\.promote(?: |$)(.*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cpromote$")
async def promote(event):
    new_rights = ChatAdminRights(
        add_admins=False,
        change_info=True,
        invite_users=True,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
        manage_call=True,
    )
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    eventren = await edit_or_reply(event, "`Promoting...`")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await eventren.edit(NO_PERM)
    await edit_delete(eventren, "`Promoted Successfully!`", 30)

@ren_cmd(pattern="demote(?:\s|$)([\s\S]*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cdemote$")
async def demote(dmod):
    # Admin right check
    chat = await dmod.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        return await dmod.edit(NO_ADMIN)

    # If passing, declare that we're going to demote
    await dmod.edit("`unadmin kontol`")
    rank = "Admin"  # dummy rank, lol.
    user = await get_user_from_event(dmod)
    user = user[0]
    if not user:
        return

    # New rights after demotion
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    # Edit Admin Permission
    try:
        await dmod.client(EditAdminRequest(dmod.chat_id, user.id, newrights, rank))

    # If we catch BadRequestError from Telethon
    # Assume we don't have permission to demote
    except BadRequestError:
        return await dmod.edit(NO_PERM)
    await dmod.edit("`Admin lepas jangan kena komtol`")
    await sleep(5)
    await dmod.delete()

    # Announce to the logging group if we have demoted successfully
    if BOTLOG:
        await dmod.client.send_message(
            BOTLOG_CHATID,
            "#MENURUNKAN\n"
            f"PENGGUNA: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {dmod.chat.title}(`{dmod.chat_id}`)",
        )


@ren_cmd(pattern="ban(?:\s|$)([\s\S]*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cban$")
async def ban(bon):
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await edit_or_reply(bon, NO_ADMIN)

    user, reason = await get_user_from_event(bon)
    if not user:
        return
    await edit_or_reply(bon, "`Whacking The Pest!`")
    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await edit_or_reply(bon, NO_PERM)
    if reason:
        await edit_or_reply(
            bon,
            r"\\**#Banned_User**//"
            f"\n\n**First Name:** [{user.first_name}](tg://user?id={user.id})\n"
            f"**User ID:** `{str(user.id)}`\n"
            f"**Reason:** `{reason}`",
        )
    else:
        await edit_or_reply(
            bon,
            f"\\\\**#Banned_User**//\n\n**First Name:** [{user.first_name}](tg://user?id={user.id})\n**User ID:** `{user.id}`\n**Action:** `Banned User by {owner}`",
        )


@ren_cmd(pattern="unban(?:\s|$)([\s\S]*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cunban$")
async def nothanos(unbon):
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await edit_delete(unbon, NO_ADMIN)
    await edit_or_reply(unbon, "`Processing...`")
    user = await get_user_from_event(unbon)
    user = user[0]
    if not user:
        return
    try:
        await unbon.client(EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await edit_delete(unbon, "`Unban Berhasil Dilakukan!`")
    except UserIdInvalidError:
        await edit_delete(unbon, "`Sepertinya Terjadi ERROR!`")


@ren_cmd(pattern="mute(?: |$)(.*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cmute$")
async def spider(spdr):
    try:
        from userbot.modules.sql_helper.spam_mute_sql import mute
    except AttributeError:
        return await edit_or_reply(spdr, NO_SQL)
    chat = await spdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await edit_or_reply(spdr, NO_ADMIN)
    user, reason = await get_user_from_event(spdr)
    if not user:
        return
    self_user = await spdr.client.get_me()
    if user.id == self_user.id:
        return await edit_or_reply(
            spdr, "**Tidak Bisa Membisukan Diri Sendiri..**"
        )
    if user.id in DEVS:
        return await edit_or_reply(spdr, "**Failed Mute, He Is My Maker**")
    await edit_or_reply(
        spdr,
        r"\\**#Muted_User**//"
        f"\n\n**First Name:** [{user.first_name}](tg://user?id={user.id})\n"
        f"**User ID:** `{user.id}`\n"
        f"**Action:** `Mute by {owner}`",
    )
    if mute(spdr.chat_id, user.id) is False:
        return await edit_delete(spdr, "**ERROR:** `Pengguna Sudah Dibisukan.`")
    try:
        await spdr.client(EditBannedRequest(spdr.chat_id, user.id, MUTE_RIGHTS))
        if reason:
            await edit_or_reply(
                spdr,
                r"\\**#DMute_User**//"
                f"\n\n**First Name:** [{user.first_name}](tg://user?id={user.id})\n"
                f"**User ID:** `{user.id}`\n"
                f"**Reason:** `{reason}`",
            )
        else:
            await edit_or_reply(
                spdr,
                r"\\**#DMute_User**//"
                f"\n\n**First Name:** [{user.first_name}](tg://user?id={user.id})\n"
                f"**User ID:** `{user.id}`\n"
                f"**Action:** `DMute by {owner}`",
            )
    except UserIdInvalidError:
        return await edit_delete(spdr, "**Terjadi ERROR!**")

@ren_cmd(outgoing=True, pattern=r"^\.unmute(?: |$)(.*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cunmute$")
async def unmoot(unmot):
    chat = await unmot.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await edit_delete(unmot, NO_ADMIN)
    try:
        from userbot.modules.sql_helper.spam_mute_sql import unmute
    except AttributeError:
        return await unmot.edit(NO_SQL)
    await edit_or_reply(unmot, "`Processing...`")
    user = await get_user_from_event(unmot)
    user = user[0]
    if not user:
        return

    if unmute(unmot.chat_id, user.id) is False:
        return await edit_delete(unmot, "**ERROR! Pengguna Sudah Tidak Dibisukan.**")
    try:
        await unmot.client(EditBannedRequest(unmot.chat_id, user.id, UNBAN_RIGHTS))
        await edit_delete(unmot, "**Berhasil Melakukan Unmute!**")
    except UserIdInvalidError:
        return await edit_delete(unmot, "**Terjadi ERROR!**")


@ren_cmd(incoming=True)
async def muter(moot):
    try:
        from userbot.modules.sql_helper.gmute_sql import is_gmuted
        from userbot.modules.sql_helper.spam_mute_sql import is_muted
    except AttributeError:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                await moot.delete()
                await moot.client(
                    EditBannedRequest(moot.chat_id, moot.sender_id, rights)
                )
    for i in gmuted:
        if i.sender == str(moot.sender_id):
            await moot.delete()


@ren_cmd(outgoing=True, pattern=r"^\.ungmute(?: |$)(.*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cungmute$")
async def ungmoot(un_gmute):
    # Admin or creator check
    chat = await un_gmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await un_gmute.edit(NO_ADMIN)

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import ungmute
    except AttributeError:
        return await un_gmute.edit(NO_SQL)

    user = await get_user_from_event(un_gmute)
    user = user[0]
    if not user:
        return

    # If pass, inform and start ungmuting
    await un_gmute.edit("```Membuka Global Mute Pengguna...```")

    if ungmute(user.id) is False:
        await un_gmute.edit("`Kesalahan! Pengguna Sedang Tidak Di Gmute.`")
    else:
        # Inform about success
        await un_gmute.edit("```Berhasil! Pengguna Sudah Tidak Lagi Dibisukan```")
        await sleep(3)
        await un_gmute.delete()

        if BOTLOG:
            await un_gmute.client.send_message(
                BOTLOG_CHATID,
                "#UNGMUTE\n"
                f"PENGGUNA: [{user.first_name}](tg://user?id={user.id})\n"
                f"GRUP: {un_gmute.chat.title}(`{un_gmute.chat_id}`)",
            )


@ren_cmd(outgoing=True, pattern=r"^\.gmute(?: |$)(.*)")
@ren_cmd(incoming=True, from_users=DEVS, pattern=r"^\.cgmute$")
async def gspider(gspdr):
    # Admin or creator check
    chat = await gspdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await gspdr.edit(NO_ADMIN)

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import gmute
    except AttributeError:
        return await gspdr.edit(NO_SQL)

    user, reason = await get_user_from_event(gspdr)
    if not user:
        return

    # If pass, inform and start gmuting
    await gspdr.edit("`Berhasil Membisukan Pengguna!`")
    if gmute(user.id) is False:
        await gspdr.edit("`Kesalahan! Pengguna Sudah Dibisukan.`")
    else:
        if reason:
            await gspdr.edit(f"**Dibisukan Secara Global!**\n**Alasan:** `{reason}`")
        else:
            await gspdr.edit("`Berhasil Membisukan Pengguna Secara Global!`")

        if BOTLOG:
            await gspdr.client.send_message(
                BOTLOG_CHATID,
                "#GLOBALMUTE\n"
                f"PENGGUNA: [{user.first_name}](tg://user?id={user.id})\n"
                f"GRUP: {gspdr.chat.title}(`{gspdr.chat_id}`)",
            )


@ren_cmd(outgoing=True, pattern=r"^\.zombies(?: |$)(.*)", groups_only=False)
async def rm_deletedacc(show):

    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "`Tidak Menemukan Akun Terhapus, Grup Bersih`"

    if con != "clean":
        await show.edit("`Mencari Akun Hantu/Terhapus/Zombie...`")
        async for user in show.client.iter_participants(show.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = (
                f"`Menemukan` **{del_u}** `Akun Hantu/Terhapus/Zombie Dalam Grup Ini,"
                "\nBersihkan Itu Menggunakan Perintah .zombies clean`")
        return await show.edit(del_status)

    # Here laying the sanity check
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        return await show.edit("`Mohon Maaf, Bukan Admin Disini!`")

    await show.edit("`Menghapus Akun Terhapus...\nMohon Menunggu Sedang Dalam Proses`")
    del_u = 0
    del_a = 0

    async for user in show.client.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                return await show.edit("`Tidak Memiliki Izin Banned Dalam Grup Ini`")
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await show.client(EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"`Membersihkan` **{del_u}** `Akun Terhapus`"

    if del_a > 0:
        del_status = (
            f"Membersihkan **{del_u}** Akun Terhapus "
            f"\n**{del_a}** `Admin Akun Terhapus Tidak Bisa Dihapus.`"
        )
    await show.edit(del_status)
    await sleep(2)
    await show.delete()

    if BOTLOG:
        await show.client.send_message(
            BOTLOG_CHATID,
            "#MEMBERSIHKAN\n"
            f"Membersihkan **{del_u}** Akun Terhapus!"
            f"\nGRUP: {show.chat.title}(`{show.chat_id}`)",
        )


@ren_cmd(outgoing=True, pattern=r"^\.admins$")
async def get_admin(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "Grup Ini"
    mentions = f"<b>✥ Daftar Admin Grup {title}:</b> \n"
    try:
        async for user in show.client.iter_participants(
            show.chat_id, filter=ChannelParticipantsAdmins
        ):
            if not user.deleted:
                link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                mentions += f"\n➤ {link}"
            else:
                mentions += f"\nAkun Terhapus <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    await show.edit(mentions, parse_mode="html")


@ren_cmd(outgoing=True, pattern=r"^\.pin(?: |$)(.*)")
async def pin(msg):
    # Admin or creator check
    chat = await msg.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await msg.edit(NO_ADMIN)

    to_pin = msg.reply_to_msg_id

    if not to_pin:
        return await msg.edit("`Mohon Balas Ke Pesan Untuk Melakukan Pin.`")

    options = msg.pattern_match.group(1)

    is_silent = True

    if options.lower() == "loud":
        is_silent = False

    try:
        await msg.client(UpdatePinnedMessageRequest(msg.to_id, to_pin, is_silent))
    except BadRequestError:
        return await msg.edit(NO_PERM)

    await msg.edit("`Berhasil Melakukan Pinned!`")
    await sleep(2)
    await msg.delete()

    user = await get_user_from_id(msg.from_id, msg)

    if BOTLOG:
        await msg.client.send_message(
            BOTLOG_CHATID,
            "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {msg.chat.title}(`{msg.chat_id}`)\n"
            f"NOTIF: {not is_silent}",
        )


@ren_cmd(outgoing=True, pattern=r"^\.kick(?: |$)(.*)")
async def kick(usr):
    # Admin or creator check
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await usr.edit(NO_ADMIN)

    user, reason = await get_user_from_event(usr)
    if not user:
        return await usr.edit("`Tidak Dapat Menemukan Pengguna.`")

    await usr.edit("`Melakukan Kick....`")

    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(0.5)
    except Exception as e:
        return await usr.edit(NO_PERM + f"\n{str(e)}")

    if reason:
        await usr.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **Telah Dikick Dari Grup**\n**Alasan:** `{reason}`"
        )
    else:
        await usr.edit(f"[{user.first_name}](tg://user?id={user.id}) **Telah Dikick Dari Grup**")
        await sleep(5)
        await usr.delete()

    if BOTLOG:
        await usr.client.send_message(
            BOTLOG_CHATID,
            "#KICK\n"
            f"PENGGUNA: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {usr.chat.title}(`{usr.chat_id}`)\n",
        )


@ren_cmd(outgoing=True, pattern=r"^\.users ?(.*)")
async def get_users(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "Grup Ini"
    mentions = "Pengguna Di {}: \n".format(title)
    try:
        if not show.pattern_match.group(1):
            async for user in show.client.iter_participants(show.chat_id):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
                else:
                    mentions += f"\nAkun Terhapus `{user.id}`"
        else:
            searchq = show.pattern_match.group(1)
            async for user in show.client.iter_participants(
                show.chat_id, search=f"{searchq}"
            ):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
                else:
                    mentions += f"\nAkun Terhapus `{user.id}`"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit("Grup Ini Terlalu Besar Mengunggah Daftar Pengguna Sebagai File.")
        file = open("daftarpengguna.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "daftarpengguna.txt",
            caption="Pengguna Dalam Grup {}".format(title),
            reply_to=show.id,
        )
        remove("daftarpengguna.txt")


async def get_user_from_event(event):
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id and len(args) != 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            return await event.edit("`Ketik Username Atau Balas Ke Pengguna!`")

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(
                    probable_user_mention_entity,
                    MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            return await event.edit(str(err))

    return user_obj, extra


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        return await event.edit(str(err))

    return user_obj


@ren_cmd(outgoing=True, pattern=r"^\.usersdel ?(.*)")
async def get_usersdel(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "Grup Ini"
    mentions = "Akun Terhapus Di {}: \n".format(title)
    try:
        if not show.pattern_match.group(1):
            async for user in show.client.iter_participants(show.chat_id):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
        #       else:
        #                mentions += f"\nAkun Terhapus `{user.id}`"
        else:
            searchq = show.pattern_match.group(1)
            async for user in show.client.iter_participants(
                show.chat_id, search=f"{searchq}"
            ):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
        #       else:
    #              mentions += f"\nAkun Terhapus `{user.id}`"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit(
            "Grup Ini Terlalu Besar, Mengunggah Daftar Akun Terhapus Sebagai File."
        )
        file = open("daftarpengguna.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "daftarpengguna.txt",
            caption="Daftar Pengguna {}".format(title),
            reply_to=show.id,
        )
        remove("daftarpengguna.txt")


async def get_userdel_from_event(event):
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id and len(args) != 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            return await event.edit("`Ketik username Atau Reply Ke Pengguna!`")

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(
                    probable_user_mention_entity,
                    MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            return await event.edit(str(err))

    return user_obj, extra


async def get_userdel_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        return await event.edit(str(err))

    return user_obj


@ren_cmd(outgoing=True, pattern=r"^\.bots$", groups_only=True)
async def get_bots(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "Grup Ini"
    mentions = f"<b>Daftar Bot Di {title}:</b>\n"
    try:
        if isinstance(show.to_id, PeerChat):
            return await show.edit("`Saya mendengar bahwa hanya Supergrup yang dapat memiliki bot`")
        else:
            async for user in show.client.iter_participants(
                show.chat_id, filter=ChannelParticipantsBots
            ):
                if not user.deleted:
                    link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                    userid = f"<code>{user.id}</code>"
                    mentions += f"\n{link} {userid}"
                else:
                    mentions += f"\nBot Terhapus <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions, parse_mode="html")
    except MessageTooLongError:
        await show.edit("Terlalu Banyak Bot Di Grup Ini, Mengunggah Daftar Bot Sebagai File.")
        file = open("botlist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "botlist.txt",
            caption="Daftar Bot Di {}".format(title),
            reply_to=show.id,
        )
        remove("botlist.txt")


CMD_HELP.update(
    {
        "admin": "𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.promote` <username/balas ke pesan> <nama title (optional)>"
        "\n↳ : Mempromosikan member sebagai admin."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.demote` <username/balas ke pesan>"
        "\n↳ : Menurunkan admin sebagai member."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.ban` <username/balas ke pesan> <alasan (optional)>"
        "\n↳ : Memblokir Seseorang."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.unban <username/reply>`"
        "\n↳ : Menghapus Blokir."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.mute` <username/balas ke pesan> <alasan (optional)>"
        "\n↳ : Membisukan Seseorang Di Grup, Bisa Ke Admin Juga."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.unmute` <username/balas ke pesan>"
        "\n↳ : Membuka bisu orang yang dibisukan."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.gmute` <username/balas ke pesan> <alasan (optional)>"
        "\n↳ : Membisukan ke semua grup yang kamu punya sebagai admin."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.ungmute` <username/reply>"
        "\n↳ : Reply someone's message with `.ungmute` to remove them from the gmuted list."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.zombies`"
        "\n↳ : Untuk mencari akun terhapus dalam grup."
        "Gunakan `.zombies clean` untuk menghapus Akun Terhapus dari grup."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.all`"
        "\n↳ : Tag semua member dalam grup."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.admins`"
        "\n↳ : Melihat daftar admin di grup."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.bots`"
        "\n↳ : Melihat daftar bot dalam grup."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.users` Atau >`.users` <nama member>"
        "\n↳ : Mendapatkan daftar pengguna daam grup."
        "\n\n𝘾𝙤𝙢𝙢𝙖𝙣𝙙: `.setgpic` <balas ke gambar>"
        "\n↳ : Mengganti foto profil grup."})
