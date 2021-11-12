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
    
@register(outgoing=True, pattern='^.war(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**WAR WAR PALAK BAPAK KAU WAR, SOK KERAS BANGET GOBLOK DI TONGKRONGAN JADI BABU DI TELE SOK JAGOAN.**")
    
@register(outgoing=True, pattern='^.dih(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**DIHH NAJISS ANAK HARAM LO GOBLOK JANGAN BELAGU DIMARI KAGA KEREN LU KEK BEGITU TOLOL.**")
    
@register(outgoing=True, pattern='^.gembel(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**MUKA BAPAK LU KEK KEPALA SAWIT ANJING, GA USAH NGATAIN ORANG, MUKA LU AJA KEK GEMBEL TEXAS GOBLOK!!.**")
    
@register(outgoing=True, pattern='^.sokab(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**SOKAB BET LU GOBLOK, KAGA ADA ISTILAH NYA BAWAHAN TEMENAN AMA BOS!!.**")
    
@register(outgoing=True, pattern='^.ded(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**MATI AJA LU GOBLOK GAGUNA LU HIDUP DI BUMI.**")
    
@register(outgoing=True, pattern='^.caper(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**NAMANYA JUGA JAMET CAPER SANA SINI BUAT CARI NAMA.**")
    
@register(outgoing=True, pattern='^.lo(?: |$)(.*)')
async def typewriter(typew):
    typew.pattern_match.group(1)
    await typew.edit("**CUIIHHH, MAKAN AJA MASIH NGEMIS LO GOBLOK, JANGAN SO NINGGI YA KONTOL GA KEREN LU KEK GITU GOBLOK.**")
    



CMD_HELP.update({
    "salam5":
    ".hekel\
    \n\n.war\
    \nUsage:\
    \n\n.dih\
    \nUsage:\
    \n\n.gembel\
    \nUsage:\
    \n\n.sokab\
    \nUsage:\
    \n\n.ded\
    \nUsage:\
    \n\n.caper\
    \nUsage:\
    \n\n.lo\
    \nUsage:"
}) 
