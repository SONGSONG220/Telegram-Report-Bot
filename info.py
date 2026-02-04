import os
import time

class Config(object):
    # Pyrogram Client
    API_ID    = int(os.environ.get("API_ID", "20394525"))  # ⚠️ Required
    API_HASH  = os.environ.get("API_HASH", "6e84bd0f4362b85dab38ede07245b16d") # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8379813954:AAEHfnxEIbSyHEco-WkqzPAAKeapB5tPaVA") # ⚠️ Required
    
    # Other Configs
    BOT_START_TIME = time.time()
    OWNER = int(os.environ.get("OWNER", "1118345061")) # ⚠️ Required

    # Web Response Config
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "8080"))

class Txt(object):

    SEND_NUMBERS_MSG = """
❪ SEND THE TOTAL NUMBER YOU HAVE ❫

☛ How many Number do You have
"""

    SEND_TARGET_CHANNEL = """
( SEND THE TARGET CHANNEL LINK or USERNAME)

☛ For e.g :- <code> @AIORFT </code> or <code> https:/t.me/AIORFT </code>
"""

    SEND_SESSION_MSG = """
❪ SEND SESSOIN STRING ❫

☛ Generate Session String form @SnowStringGenBot


"""

    SEND_API_ID = """
❪ SEND API ID ❫

☛ Api_id Get from my.telegram.org
"""
    SEND_API_HASH = """
❪ SEND API HASH ❫

☛ Api_hash Get from my.telegram.org
"""

    MAKE_CONFIG_DONE_MSG = """
Your {} accounts has been added 👥

And Logined to the Target Channel/Group to Report it. ✅

➜ Click the button bellow to see the Number of Telegram account you added.
"""

    ADDED_ACCOUNT = """
Your have added {} accounts 👥

➜ Click the button bellow to see the More Info of the Telegram accounts which you haved added.
"""

    ACCOUNT_INFO = """
<b> Name :- </b> <code> {0} </code>
<b> User Id :- </b> <code> {1} </code>
"""

    REPORT_CHOICE = """
❪ SELECT REASON FOR REPORT 👤 ❫

1. Report for child abuse
2. Report for copyrighted content
3. Report for impersonation
4. Report an irrelevant geogroup
5. Report an illegal durg
6. Report for Violence
7. Report for offensive person detail
8. Reason for Pornography
9. Report for spam

Whats your  reason: select 1-9 👇 
"""

    SEND_NO_OF_REPORT_MSG = """
❪ SELECT NUMBER OF REPORTS 👤 ❫

**Send Number of reports which you want to report to this @{}**

The bot will keep reporting to target channel or group until it's reach the number of report. 🎯
"""

    START_MSG = """
Hɪ {},

Tʜɪs Bᴏᴛ ɪs ғᴏʀ ᴛᴏ ʀᴇᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ ɪɴ ᴍᴀss ʟᴇᴠᴇʟ ᴛʜʀᴏᴜɢʜ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ sᴇssɪᴏɴ sᴛʀɪɴɢ ᴡʜɪᴄʜ ʏᴏᴜ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ʙʏ @SnowStringGenBot.

Tʜɪs ʙᴏᴛ ɪs sᴏʟᴇʟʏ ᴄʀᴇᴀᴛᴇ ᴏʀ ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ :- @urstarkz
"""

    HELP_MSG = """
🔆 HELP

📚 Available commands:
⏣ /start - check I'm alive 
⏣ /make_config - To Make Config 
⏣ /del_config - Delete the Config
⏣ /target - To see the target channel
⏣ /see_accounts - See all the accounts you added
⏣ /add_account - Add new accounts
⏣ /report - Report the target
⏣ /restart - Restart the bot

💢 Features:
► Report a single channel or group with multiple Id's
► Type of report option available
► Facilitie to change the Target Channel or Group
► Facilitie to add the multiples accounts after once you make config
► All the accounts you added will automatically joined the target channel or group
► No need to enter phone number, password or otp just send session string and that's it
► Check the server status and resources
"""

    ABOUT_MSG = """
- 𝖬𝗒 𝖭𝖺𝗆𝖾 : <a href=https://t.me/{}>{}</a>
- 𝖢𝗋𝖾𝖺𝗍𝗈𝗋 : <a href=https://t.me/urstarkz>STARK</a>
- 𝖫𝗂𝖻𝗋𝖺𝗋𝗒 : Pyrogram
- 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 : 𝖯𝗒𝗍𝗁𝗈𝗇 𝟥
- 𝖣𝖺𝗍𝖺𝖡𝖺𝗌𝖾 : 𝖬𝗈𝗇𝗀𝗈𝖣𝖡
- 𝖡𝖮𝖳 𝖲𝖾𝗋𝗏𝖾𝗋 : 𝖠𝗇𝗒𝖶𝗁𝖾𝗋𝖾
"""
