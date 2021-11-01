# Gausah kesini ngentot!!
# NGEDIT CMD YG BENER KONTOL!!!


from platform import uname
from userbot import ALIVE_NAME, CMD_HELP
from userbot.events import register

# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
# ============================================

@register(outgoing=True, pattern='^.a(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**𝐀NJING LO MUKA KONTOL.**")
















    


CMD_HELP.update({
    "salam5":
    ".a\
\nUsage:\
\n\n.u\
\nUsage:\
\n\n.kn\
\nUsage:\
\n\n.tk\
\nUsage:\
\n\n.hekel\
\nUsage:\
\n\n.ds\
\nUsage:\
\n\n.t\
\nUsage:"
})

