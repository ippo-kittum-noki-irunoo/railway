# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, CH_FILTER, CH_LINK, MAX_RESULT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,




)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
FILTER_MODE = {}
SELECTED_FILES = {}


@Client.on_message(filters.command('autofilter'))
async def fil_mod(client, message): 
      mode_on = ["yes", "on", "true"]
      mode_of = ["no", "off", "false"]

      try: 
         args = message.text.split(None, 1)[1].lower() 
      except: 
         return await message.reply("**𝙸𝙽𝙲𝙾𝙼𝙿𝙻𝙴𝚃𝙴 𝙲𝙾𝙼𝙼𝙰𝙽𝙳...**")
      
      m = await message.reply("**𝚂𝙴𝚃𝚃𝙸𝙽𝙶.../**")

      if args in mode_on:
          FILTER_MODE[str(message.chat.id)] = "True" 
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙴𝙽𝙰𝙱𝙻𝙴𝙳**")
      
      elif args in mode_of:
          FILTER_MODE[str(message.chat.id)] = "False"
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙳𝙸𝚂𝙰𝙱𝙻𝙴𝙳**")
      else:
          await m.edit("𝚄𝚂𝙴 :- /autofilter on 𝙾𝚁 /autofilter off")




@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    _, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("😁 𝗛𝗲𝘆 𝗙𝗿𝗶𝗲𝗻𝗱,𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗮𝗿𝗰𝗵 𝗬𝗼𝘂𝗿𝘀𝗲𝗹𝗳.", show_alert=True)

    selecting_files = False

    if len(offset.split("#")) > 1:
        offset, ident = offset.split("#")
        if ident == "Exit":
            del SELECTED_FILES[key]
        elif ident == "slctng":
            selecting_files = True


    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("𝐋𝐢𝐧𝐤 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 𝐊𝐢𝐧𝐝𝐥𝐲 𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐞𝐚𝐫𝐜𝐡 𝐀𝐠𝐚𝐢𝐧 🙂.", show_alert=True)
        return

    files, next_offset, total = await get_search_results(search, offset=offset, filter=True)

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    slctd_files = SELECTED_FILES.get(key, {}).get(offset, [])
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text="✔️" if selecting_files and i in slctd_files else f"🎥[{get_size(file.file_size)}]🎬 {file.file_name}", 
                    callback_data=f'files#{file.file_id}' if not selecting_files 
                        else (f"selected_file#{key}#{req}#{offset}#{i}" if i not in slctd_files 
                        else f"ignore")
                ),
            ]
            for i, file in enumerate(files)
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text="✔️" if selecting_files and i in slctd_files else f"{file.file_name}", 
                    callback_data=f'files#{file.file_id}' if not selecting_files 
                        else (f"selected_file#{key}#{req}#{offset}#{i}" if i not in slctd_files 
                        else f"ignore")
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}'if not selecting_files 
                        else (f"selected_file#{key}#{req}#{offset}#{i}" if i not in slctd_files 
                        else f"ignore")
                ),
            ]
            for i, file in enumerate(files)
        ]

    if selecting_files:
        btn.append(
            [
                InlineKeyboardButton("Exit", callback_data=f"next_{req}_{key}_{offset}#Exit"),
                InlineKeyboardButton("Send", callback_data=f"send_files#{key}#{req}"),
            ]
        )
    else:
        btn.insert(
            0, [
            InlineKeyboardButton("All", callback_data=f'send_all#{key}#{req}#{offset}'),
            InlineKeyboardButton(f'Files: {len(files)}', 'reqst1'),
            InlineKeyboardButton("Select", callback_data=f'select_files#{key}#{req}#{offset}'),
            ]
        )

    if 0 < offset <= MAX_RESULT:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - MAX_RESULT

    if next_offset == 0 or offset + MAX_RESULT == total:
        btn.append(
            [InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}" + ("#slctng" if selecting_files else "")),
             InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}", callback_data="pages"),
             InlineKeyboardButton("𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{next_offset}" + ("#slctng" if selecting_files else ""))])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}" + ("#slctng" if selecting_files else "")),
                InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}", callback_data="pages"),
                InlineKeyboardButton("𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{next_offset}" + ("#slctng" if selecting_files else ""))
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()



@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("okDa", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit('This Movie Not Found In DataBase')
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('Piracy Is Crime')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('Piracy Is Crime')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('Piracy Is Crime')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('Piracy Is Crime')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        type = files.file_type
        mention = query.from_user.mention
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
                                                       
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
            size = size
            mention = mention
        if f_caption is None:
            f_caption = f"{files.file_name}"
            size = f"{files.file_size}"
            mention = f"{query.from_user.mention}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                ms = await client.send_cached_media(
                    chat_id=CH_FILTER,
                    file_id=file_id,
                    caption=f'<b><i>📟 Name : <a href=https://t.me/+hpnKBqJC_cQ3ZjU1>{title}</a></i></b>\n\n<b><i>🎗 Size : {size}</b></i>\n\n<i>⚠️ This Message Will Be Auto-Deleted In Next 5 Minutes T𝘰 Avoid Copyright Issues.So Forward This File To Anywhere Else Before Downloading.. ⚠️</i>\n\n<b><i>🧑🏻‍💻 Requested By : {query.from_user.mention}\n🚀 Group : {query.message.chat.title}</i></b>',
                    protect_content=True if ident == "filep" else False 
                )
                msg1 = await query.message.reply(
                f'<b><i>{query.from_user.mention} Your File Is Ready ✨</i></b>\n\n'
                f'<b><i>📟 Name : <a href=https://t.me/+hpnKBqJC_cQ3ZjU1>{title}</a></i></b>\n\n'
                f'<b><i>🎗 Size : {size}</b></i>\n\n'
                '<i>⚡️Click The Below Button For Files.⚡️</i>',
                True,
                'html',
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("ᴄʟɪᴄᴋ ʜᴇʀᴇ ғᴏʀ ғɪʟᴇ", url = ms.link)
                        ],
                        [
                            InlineKeyboardButton("ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴊᴏɪɴ ғɪʟᴇs ᴄʜᴀɴɴᴇʟ", url = f"{CH_LINK}")
                        ]
                    ]
                )
            )
            await asyncio.sleep(300)
            await msg1.delete()            
            await ms.delete()
            del msg1, ms
        except Exception as e:
            logger.exception(e, exc_info=True)

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer(f"Hey, {query.from_user.first_name}! I Like Your Smartness, But Don't Be Oversmart 😒",show_alert=True)
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer(f'Hello, {query.from_user.first_name}! No such file exist. Send Request Again')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        ms = await client.send_cached_media(
            chat_id=CH_FILTER,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        ) 
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
             InlineKeyboardButton('✣ 𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚈𝙾𝚄𝚁 𝙶𝚁𝙾𝚄𝙿 ✣', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('❉𝙲𝙷𝙰𝙽𝙽𝙴𝙻❉', url='https://t.me/+hpnKBqJC_cQ3ZjU1'),
            InlineKeyboardButton(' ❈𝙶𝚁𝙾𝚄𝙿❈ ', url='https://t.me/+JLuNC2rGfgQ0OGRl')
            ],[      
            InlineKeyboardButton('✹𝙷𝙴𝙻𝙿✹', callback_data='help'),
            InlineKeyboardButton(' ✺𝙰𝙱𝙾𝚄𝚃✺ ', callback_data='about')
            ],[
            InlineKeyboardButton(' ✻𝚂𝙴𝙰𝚁𝙲𝙷 𝙷𝙴𝚁𝙴✻ ', switch_inline_query_current_chat='')
            ],[
            InlineKeyboardButton(' ✼𝙱𝙰𝙲𝙺 𝚃𝙾 𝙼𝙴𝙽𝚄 ✼', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Manual Filter', callback_data='manuelfilter'),
            InlineKeyboardButton('Auto Filter', callback_data='autofilter')
        ], [
            InlineKeyboardButton('Connection', callback_data='coct'),
            InlineKeyboardButton('Extra Mods', callback_data='extra')
        ], [
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔮 Status', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('⏹️ Buttons', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "movss":
        await query.answer("👉ഗ്രൂപ്പിൽ ജോയിൻ ചെയ്തതിനു ശേഷം, ആവിശ്യം ഉള്ള സിനിമ ചോദിക്കുക. ബോട്ട് സിനിമ അയച്ചു തരുന്നത് ആകും. എന്തേലും ഇഷ്യൂ ഉണ്ടേൽ OWNERന് മെസ്സേജ് ചെയ്യുക.എല്ലാവരും സഹകരിക്കുക.🤝", show_alert=True)
        
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('👮‍♂️ Admin', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
               [
                    InlineKeyboardButton('𝐅𝐈𝐋𝐓𝐄𝐑 𝐁𝐔𝐓𝐓𝐎𝐍',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('𝐒𝐈𝐍𝐆𝐋𝐄' if settings["button"] else '𝐃𝐎𝐔𝐁𝐋𝐄',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐁𝐎𝐓 𝐏𝐌', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["botpm"] else '🗑️ 𝐍𝐎',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐅𝐈𝐋𝐄 𝐒𝐄𝐂𝐔𝐑𝐄',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["file_secure"] else '🗑️ 𝐍𝐎',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐈𝐌𝐃𝐁', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["imdb"] else '🗑️ 𝐍𝐎',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐒𝐏𝐄𝐋𝐋 𝐂𝐇𝐄𝐂𝐊',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["spell_check"] else '🗑️ 𝐍𝐎',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐖𝐄𝐋𝐂𝐎𝐌𝐄', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["welcome"] else '🗑️ 𝐍𝐎',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('Piracy Is Crime')
 # All and Select Button Callbacks
    elif query.data.startswith("send_all"):
        
        _, key, req, offset = query.data.split("#")

        if int(req) not in [query.from_user.id, 0]:
            return await query.answer("😁 𝗛𝗲𝘆 𝗙𝗿𝗶𝗲𝗻𝗱,𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗮𝗿𝗰𝗵 𝗬𝗼𝘂𝗿𝘀𝗲𝗹𝗳.", show_alert=True)

        try:
            msg = await client.send_message(query.from_user.id, ".")
            await msg.delete()
        except Exception:
            await query.answer("Please start my pm to continue.", show_alert=True)
            return await query.answer(url="https://t.me/{}".format(temp.U_NAME))

        try:
            offset = int(offset)
        except:
            offset = 0
        
        search = BUTTONS.get(key)
        if not search:
            await query.answer("𝐋𝐢𝐧𝐤 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 𝐊𝐢𝐧𝐝𝐥𝐲 𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐞𝐚𝐫𝐜𝐡 𝐀𝐠𝐚𝐢𝐧 🙂.", show_alert=True)
            return

        files, nxt_offset, total = await get_search_results(search.lower(), offset=offset, filter=True)
        if not files:
            return

        settings = await get_settings(query.message.chat.id)

        if settings['botpm']:
            chat_id=query.from_user.id
        else:
            chat_id=CH_FILTER

        for file in files:
            await client.send_cached_media(
                chat_id=chat_id,
                file_id=file.file_id,
                caption=file.caption,
                parse_mode="HTML",
                protect_content= False if settings['file_secure'] == 'file' else True
            )
            await asyncio.sleep(0.5)

        await query.answer(f"Movie/Series: {search}, Page: {round(int(offset) / MAX_RESULT) + 1} Files: {len(files)}")

    elif query.data.startswith("select_files"):

        _, key, req, offset = query.data.split("#")

        if int(req) not in [query.from_user.id, 0]:
            return await query.answer("😁 𝗛𝗲𝘆 𝗙𝗿𝗶𝗲𝗻𝗱,𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗮𝗿𝗰𝗵 𝗬𝗼𝘂𝗿𝘀𝗲𝗹𝗳.", show_alert=True)

        try:
            msg = await client.send_message(query.from_user.id, ".")
            await msg.delete()
        except Exception:
            await query.answer("Please start my pm to continue.", show_alert=True)
            return await query.answer(url="https://t.me/{}".format(temp.U_NAME))

        try:
            offset = int(offset)
        except:
            offset = 0
        
        search = BUTTONS.get(key)
        if not search:
            await query.answer("𝐋𝐢𝐧𝐤 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 𝐊𝐢𝐧𝐝𝐥𝐲 𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐞𝐚𝐫𝐜𝐡 𝐀𝐠𝐚𝐢𝐧 🙂.", show_alert=True)
            return
        
        files, nxt_offset, total = await get_search_results(search.lower(), offset=offset, filter=True)
        if not files:
            return

        settings = await get_settings(query.message.chat.id)
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"🎥[{get_size(file.file_size)}]🎬 {file.file_name}", callback_data=f'selected_file#{key}#{req}#{offset}#{i}'
                    ),
                ]
                for i, file in enumerate(files)
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        callback_data=f'selected_file#{key}#{req}#{offset}#{i}',
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'selected_file#{key}#{req}#{offset}#{i}',
                    ),
                ]
                for i, file in enumerate(files)
            ]


        if 0 < offset <= MAX_RESULT:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - MAX_RESULT

        btn.append(
            [
                InlineKeyboardButton("Exit", callback_data=f"next_{req}_{key}_{offset}#Exit"),
                InlineKeyboardButton("Send", callback_data=f"send_files#{key}#{req}"),
            ]
        )

        if nxt_offset == 0 or offset + MAX_RESULT == total:
            btn.append(
                [InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}#slctng"),
                InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}",
                                    callback_data="pages")]
            )
        elif off_set is None:
            btn.append(
                [InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}", callback_data="pages"),
                InlineKeyboardButton("𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{nxt_offset}#slctng")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}#slctng"),
                    InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}", callback_data="pages"),
                    InlineKeyboardButton("𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{nxt_offset}#slctng")
                ],
            )
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()

    elif query.data.startswith("selected_file"):
            
        _, key, req, offset, i = query.data.split("#")

        if int(req) not in [query.from_user.id, 0]:
            return await query.answer("😁 𝗛𝗲𝘆 𝗙𝗿𝗶𝗲𝗻𝗱,𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗮𝗿𝗰𝗵 𝗬𝗼𝘂𝗿𝘀𝗲𝗹𝗳.", show_alert=True)

        try:
            offset = int(offset)
            i = int(i)
        except:
            offset = 0
            i = int(i)
        
        search = BUTTONS.get(key)
        if not search:
            await query.answer("𝐋𝐢𝐧𝐤 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 𝐊𝐢𝐧𝐝𝐥𝐲 𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐞𝐚𝐫𝐜𝐡 𝐀𝐠𝐚𝐢𝐧 🙂.", show_alert=True)
            return
        
        files, nxt_offset, total = await get_search_results(search.lower(), offset=offset, filter=True)
        if not files:
            return

        if not SELECTED_FILES.get(key, False):
            SELECTED_FILES[key] = {}

        settings = await get_settings(query.message.chat.id)
        btn = []

        for j, file in enumerate(files):

            if not SELECTED_FILES[key].get(offset, False):
                SELECTED_FILES[key][offset] = []
            if j == i:
                SELECTED_FILES[key][offset].append(j)

            slctd_list = SELECTED_FILES[key][offset]
            selected = i == j or j in slctd_list

            if settings["button"]:

                text = "✔️" if selected else f"🎥[{get_size(file.file_size)}]🎬 {file.file_name}"
                btn += [
                    [
                        InlineKeyboardButton(
                            text=text, callback_data=f'ignore' if selected else f'selected_file#{key}#{req}#{offset}#{j}'
                        ),
                    ]
                ]
            else:
                text = "✔️" if selected else f"{file.file_name}"
                btn += [
                    [
                        InlineKeyboardButton(
                            text=text, callback_data=f'ignore' if selected else f'selected_file#{key}#{req}#{offset}#{j}'
                        ),
                        InlineKeyboardButton(
                            text=f"{get_size(file.file_size)}", callback_data=f'ignore' if selected else f'selected_file#{key}#{req}#{offset}#{j}'
                        )
                    ]
                ]

        
        if 0 < offset <= MAX_RESULT:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - MAX_RESULT

        btn.append(
            [
                InlineKeyboardButton("Exit", callback_data=f"next_{req}_{key}_{offset}#Exit"),
                InlineKeyboardButton("Send", callback_data=f"send_files#{key}#{req}"),
            ]
        )

        if nxt_offset == 0 or offset + MAX_RESULT == total:
            btn.append(
                [InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}#slctng"),
                InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}",
                                    callback_data="pages")]
            )
        elif off_set is None:
            btn.append(
                [InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}", callback_data="pages"),
                InlineKeyboardButton("𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{nxt_offset}#slctng")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}#slctng"),
                    InlineKeyboardButton(f"🎭 𝗣𝗮𝗴𝗲 {round(int(offset) / MAX_RESULT) + 1} / {round(total / MAX_RESULT)}", callback_data="pages"),
                    InlineKeyboardButton("𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{nxt_offset}#slctng")
                ],
            )
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()

    elif query.data.startswith("send_files"):

        _, key, req = query.data.split("#")
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer("😁 𝗛𝗲𝘆 𝗙𝗿𝗶𝗲𝗻𝗱,𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗮𝗿𝗰𝗵 𝗬𝗼𝘂𝗿𝘀𝗲𝗹𝗳.", show_alert=True)

        slctd_files = SELECTED_FILES.get(key, False)
        search = BUTTONS.get(key, False)
        if not slctd_files or not search:
            await query.answer("Request 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 𝐊𝐢𝐧𝐝𝐥𝐲 𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐞𝐚𝐫𝐜𝐡 𝐀𝐠𝐚𝐢𝐧 🙂.", show_alert=True)
            return
        
        settings = await get_settings(query.message.chat.id)

        if settings['botpm']:
            chat_id=query.from_user.id
        else:
            chat_id=CH_FILTER
        try:
            for offset in slctd_files:
                files, _, __ = await get_search_results(search.lower(), offset=offset, filter=True)
                for i in slctd_files[offset]:
                    file = files[i]
                    await client.send_cached_media(
                        chat_id=chat_id,
                        file_id=file.file_id,
                        caption=file.caption,
                        parse_mode="HTML",
                        protect_content= False if settings['file_secure'] == 'file' else True
                    )
                    await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(e)
            return await query.answer("Couldn't send files, please try again later.", show_alert=True)
        else:
            await query.answer("🎉 Check your pm for the files 🎉")
            return


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, next_offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, next_offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"🎥[{get_size(file.file_size)}]🎬 {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}_#{file.file_id}',
                ),
            ]
            for file in files
        ]
    
    key = f"{message.chat.id}-{message.message_id}"
    req = message.from_user.id if message.from_user else 0
    BUTTONS[key] = search

    btn.insert(
        0, [
        InlineKeyboardButton("All", callback_data=f'send_all#{key}#{req}#{0}'),
        InlineKeyboardButton(f'Files: {len(files)}', 'reqst1'),
        InlineKeyboardButton("Select", callback_data=f'select_files#{key}#{req}#{0}'),
        ]
    )

    if total_results > MAX_RESULT:
        btn.append(
            [InlineKeyboardButton(text=f"🎭 𝗣𝗮𝗴𝗲 1/{round(int(total_results) / MAX_RESULT)}", callback_data="pages"),
             InlineKeyboardButton(text="𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{next_offset}")]
        )
        btn = [ 
            [
                InlineKeyboardButton(f'🎬 {search} 🎬', url='https://t.me/+JLuNC2rGfgQ0OGRl')
            ]
        ] + btn

    else:
        btn.append(
            [InlineKeyboardButton(text="🎭 𝗣𝗮𝗴𝗲 1/1", callback_data="pages")]
        )

    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"Hello {message.from_user.mention} നിങ്ങൾ ഗ്രൂപ്പിൽ ചോദിച്ച {search} എന്ന സിനിമയുടെ ലിസ്റ്റ് താഴെ കൊടുത്തിട്ട് ഉണ്ട്. ആദ്യത്തെ ലിസ്റ്റിൽ ഇല്ലങ്കിൽ സിനിമ NEXT » ബട്ടൺ ക്ലിക്ക് ചെയ്തു അടുത്ത പേജ് കൂടെ നോക്കുക. #Press How To Download"
    if imdb and imdb.get('poster'):
        try:
            fmsg = await message.reply_photo('https://telegra.ph/file/2852538a958144259930b.jpg', caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("I couldn't find any movie in that name.")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("I couldn't find anything related to that. Check your spelling")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await msg.reply("I couldn't find anything related to that\nDid you mean any one of these?",
                    reply_markup=InlineKeyboardMarkup(btn))


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
