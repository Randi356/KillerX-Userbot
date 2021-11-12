# Gausah kesini ngentot!!
# NGEDIT CMD YG BENER KONTOL!!!
# OWN MY CODE RENDY


from platform import uname
from userbot import ALIVE_NAME, CMD_HELP
from userbot.events import register

# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
# ============================================

@register(outgoing=True, pattern='^.hekel(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**SAYA GANTENG HEKEL BOS YAHAHAHA KONTOL.**")
    



CMD_HELP.update({
    "salam5":
    ".hekel\
\nUsage:"
}) 
