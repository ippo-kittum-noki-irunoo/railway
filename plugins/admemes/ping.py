"""Telegram Ping / Pong Speed
Syntax: .ping"""

import time
import random
from pyrogram import Client, filters
from info import COMMAND_HAND_LER
from plugins.helper_functions.cust_p_filters import f_onw_fliter

# -- Constants -- #
ALIVE = "ചത്തിട്ടില്ല മുത്തേ ഇവിടെ തന്നെ ഉണ്ട്.. നിനക്ക് ഇപ്പൊ എന്നോട് ഒരു സ്നേഹവും ഇല്ല. കൊള്ളാം.. നീ പാഴെ പോലെയേ അല്ല മാറിപോയി..😔 ഇടക്ക് എങ്കിലും ചുമ്മാ ഒന്ന് /start ചെയ്തു നോക്ക്..🙂" 
REPO =  "Ahda mone ippo kittum noki irunoo"
CHANNEL = "<b>𝖦𝗋𝗈𝗎𝗉</b> ›› https://t.me/+JLuNC2rGfgQ0OGRl\n\n<b>𝖡𝗈𝗍 𝚄𝙿𝙳𝙰𝚃𝙴𝚂 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 ›› https://t.me/+E4c_SeycYe8wOWE1</b>\n\n<b>𝙲𝙷𝙰𝙽𝙽𝙴𝙻 ›› https://t.me/+hpnKBqJC_cQ3ZjU1</b>"
BOT = "<b>𝙱𝙾𝚃 ›› https://t.me/Hichozbot</b>"
# -- Constants End -- #


@Client.on_message(filters.command("alive", COMMAND_HAND_LER) & f_onw_fliter)
async def check_alive(_, message):
    await message.reply_text(ALIVE)


@Client.on_message(filters.command("ping"))
async def ping(_, message):
    start_t = time.time()  
    avr = await message.reply_text("•••")  
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    uptime = time.strftime("%Hh | %Mm | %Ss", time.gmtime(time.time() - BOT_START_TIME))   
    await avr.edit(f"-ᴄᴜʀʀᴇɴᴛ ʙᴏᴛ sᴛᴀᴛᴜs-\n\n 🏓 ᴘᴏɴɢ : {time_taken_s:.3f} ms\n\n ⏰ ᴜᴘᴛɪᴍᴇ : {uptime}")
    await asyncio.sleep(DELETE_TIME)
    await avr.delete()

@Client.on_message(filters.command("repo", COMMAND_HAND_LER) & f_onw_fliter)
async def repo(_, message):
    await message.reply_text(REPO)


@Client.on_message(filters.command("group", COMMAND_HAND_LER) & f_onw_fliter)
async def group(_, message):
    await message.reply_text(GROUP)


@Client.on_message(filters.command("channel", COMMAND_HAND_LER) & f_onw_fliter)
async def channel(_, message):
    await message.reply_text(CHANNEL)


@Client.on_message(filters.command("ajax", COMMAND_HAND_LER) & f_onw_fliter)
async def ajax(_, message):
    await message.reply_text(AJAX)


