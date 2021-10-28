from platform import uname
from userbot import ALIVE_NAME, CMD_HELP
from userbot.events import register

# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
# ============================================

@register(outgoing=True, pattern='^T(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**TOLOL ANJING!!**")


CMD_HELP.update({
    "salam5":
    "T\
\nUsage: tolol.\
})

