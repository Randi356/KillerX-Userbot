""" Userbot module for other small commands. """
from userbot import CMD_HELP, ALIVE_NAME
from userbot.events import register


# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
# ============================================


@register(outgoing=True, pattern="^.helpmy$")
async def usit(e):
    await e.edit(
        f"**Hai {DEFAULTUSER} Kalau Anda Tidak Tau Perintah Untuk Memerintah Ku Ketik** `.xhelp` Atau Bisa `.help` atau Minta Bantuan Ke:\n"
        "\n[GSAHMANJA](t.me/gsahmanja)"
        "\n\n[SUPPORT](https://t.me/RemixSupport)"
        "\n\n[CHANNEL](https://t.me/codersUpdates)")


@register(outgoing=True, pattern="^.rvars$")
async def var(m):
    await m.edit(
        f"**Disini Daftar Vars Dari {DEFAULTUSER}:**\n"
        "\n[DAFTAR VARS](https://raw.githubusercontent.com/Randi356/Vegeta-Userbot/Vegeta-Userbot/varshelper.txt)")


CMD_HELP.update({
    "chillyhelper":
    "`.helpmy`\
\nPenjelasan: Bantuan Untuk Vegeta-Userbot.\
\n`.rvars`\
\nPenjelasan: Untuk Melihat Beberapa Daftar Vars."
})
