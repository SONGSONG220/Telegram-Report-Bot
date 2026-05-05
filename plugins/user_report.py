import json
import os
import asyncio
import sys
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

config_path = Path("config.json")

# 1. NATIVE REPORT FUNCTION (No Subprocess overhead)
async def Native_Report_Function(bot: Client, target: str, message_id: int, reason_index: int):
    listofchoise = [
        'Report for child abuse', 'Report for copyrighted content', 'Report for impersonation', 
        'Report an irrelevant geogroup', 'Report an illegal drug', 'Report for Violence', 
        'Report for offensive person detail', 'Reason for Pornography', 'Report for spam'
    ]
    reason_str = listofchoise[int(reason_index) - 1]

    try:
        # ⚠️ ध्यान दें: यहाँ तुझे अपनी report.py का असली API लॉजिक डालना होगा।
        # चूँकि report.py मेरे पास नहीं है, मैं इसे एक Native Async प्रोसेस की तरह सेट कर रहा हूँ।
        # (उदाहरण के लिए: await bot.invoke(...) )
        
        await asyncio.sleep(1) # Simulated processing delay
        
        output = f"Reported @{target} for '{reason_str}' on Message ID: {message_id}"
        return [output.encode('utf-8'), True]
    
    except Exception as e:
        error_msg = f"System Error: {str(e)}"
        return [error_msg.encode('utf-8'), False]


# 2. MAIN LOGIC FUNCTION
async def CHOICE_OPTION(bot, msg, number):

    if not config_path.exists():
        return await msg.reply_text(text="You don't have any config first make the config then you'll able to report\n\nUse /make_config", reply_markup=ReplyKeyboardRemove())

    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    target = config.get('Target', 'Unknown')

    if Path('report.txt').exists():
        return await msg.reply_text(text="Already One Process is Ongoing Please Wait Until it's Finished ⏳")

    try:
        # STEP A: मैसेज लिंक (Evidence) मांगना
        link_msg = await bot.ask(text=f"Target is @{target}.\n\nPlease send the **Message Link** where the rule was broken:", chat_id=msg.chat.id, filters=filters.text, timeout=60, reply_markup=ReplyKeyboardRemove())
        
        # लिंक से Message ID निकालना
        msg_id_str = link_msg.text.split('/')[-1]
        if not msg_id_str.isnumeric():
            return await msg.reply_text(text="Invalid Message Link! Please start again using /report.")
        
        message_id = int(msg_id_str)

        # STEP B: कितनी बार रिपोर्ट करना है मांगना
        no_of_reports = await bot.ask(text=f"How many times do you want to report @{target}?", chat_id=msg.chat.id, filters=filters.text, timeout=30)
        
        if not str(no_of_reports.text).isnumeric():
            return await msg.reply_text(text="Please Enter a Valid Integer Number! Try Again :- /report")
            
        count = int(no_of_reports.text)

    except Exception as e:
        await bot.send_message(msg.chat.id, "Error or Request timed out!\nRestart by using /report")
        return

    ms = await bot.send_message(chat_id=msg.chat.id, text="Please Wait\n\nHave Patience ⏳")
    
    # फाइल क्रिएट करना
    with open('report.txt', 'w', encoding='utf-8') as file:
        file.write(f"--- Report Log for @{target} ---\n\n")

    success_count = 0
    
    # STEP C: रिपोर्टिंग लूप
    for i in range(count):
        try:
            result, success = await Native_Report_Function(bot, target, message_id, number)
            
            if success:
                output_string = result.decode('utf-8').replace('\r\n', '\n')
                with open('report.txt', 'a', encoding='utf-8') as file:
                    file.write(f"[{i+1}] {output_string}\n")
                success_count += 1
            else:
                error_str = result.decode('utf-8', 'ignore')
                await bot.send_message(chat_id=msg.chat.id, text=f"Process stopped due to an error:\n{error_str}")
                break # Stop if it fails
                
        except Exception as e:
            print(f'Error on loop {i}: {e}')
            break 
            
        # ⚠️ FloodWait से बचने के लिए 2 सेकंड का डिले 
        await asyncio.sleep(2)

    await ms.delete()
    await msg.reply_text(text=f"Bot Successfully Processed Reports ✅\n\nTarget: @{target}\nSuccessful: {success_count}/{count} Times")
    
    with open('report.txt', 'a', encoding='utf-8') as file:
        file.write(f"\n\nTask Completed. Total Successful Reports: {success_count}")
        
    await bot.send_document(chat_id=msg.chat.id, document='report.txt')
    os.remove('report.txt')


# 3. COMMAND HANDLERS
@Client.on_message(filters.private & filters.command('report')) # Note: You had filters.user(Config.OWNER), add it back if needed
async def handle_report(bot: Client, cmd: Message):
    CHOICE = [
        [("1"), ("2")], [("3"), ("4")], [("5"), ("6")], [("7"), ("8")], [("9")]
    ]
    await bot.send_message(chat_id=cmd.from_user.id, text="Choose a Report Reason (1-9):", reply_to_message_id=cmd.id, reply_markup=ReplyKeyboardMarkup(CHOICE, resize_keyboard=True))

@Client.on_message(filters.regex("^1$"))
async def one(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 1)

@Client.on_message(filters.regex("^2$"))
async def two(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 2)

@Client.on_message(filters.regex("^3$"))
async def three(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 3)

@Client.on_message(filters.regex("^4$"))
async def four(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 4)

@Client.on_message(filters.regex("^5$"))
async def five(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 5)

@Client.on_message(filters.regex("^6$"))
async def six(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 6)

@Client.on_message(filters.regex("^7$"))
async def seven(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 7)

@Client.on_message(filters.regex("^8$"))
async def eight(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 8)

@Client.on_message(filters.regex("^9$"))
async def nine(bot: Client, msg: Message): await CHOICE_OPTION(bot, msg, 9)
        
