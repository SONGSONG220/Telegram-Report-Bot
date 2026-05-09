import json
import os
import subprocess
import sys
import asyncio
import time
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from info import Config, Txt

config_path = Path("config.json")

# Crime message templates user select kar sakta hai
CRIME_MESSAGES = {
    "1": "This account is spreading spam and scam links in multiple groups.",
    "2": "This account is impersonating a legitimate person or brand.",
    "3": "This account is sharing illegal and copyrighted content without permission.",
    "4": "This account is involved in fraud and financial scams.",
    "5": "This account is sharing violent and harmful content.",
    "6": "This account is sharing child abuse content which is illegal.",
    "7": "This account is sharing pornography and adult content without consent.",
    "8": "This account is promoting illegal drugs and substances.",
    "9": "This account is sharing personal details of others without permission."
}


async def Report_Round(reason_number, crime_message):
    """Ek round me saare accounts se report with custom crime message"""
    
    listofchoise = [
        'Report for child abuse', 'Report for copyrighted content', 
        'Report for impersonation', 'Report an irrelevant geogroup',
        'Report an illegal durg', 'Report for Violence', 
        'Report for offensive person detail', 'Reason for Pornography', 
        'Report for spam'
    ]
    message = listofchoise[int(reason_number) - 1]

    print(f"🚀 Starting report round | Reason: {message} | Crime: {crime_message[:50]}...")
    
    # Report script ko crime message ke saath call karo
    process = subprocess.Popen(
        ["python", "report.py", message, crime_message],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate()
    return_code = process.wait()

    print(stdout)
    if stderr:
        print(f"STDERR: {stderr}")

    if return_code == 0:
        return [stdout, True]
    else:
        return [f"<b>Error Occurred!</b>\n\n<code>{stderr}</code>", False]


async def CHOICE_OPTION(bot, msg, number):
    """5 accounts se auto-report with crime message"""

    if not config_path.exists():
        return await msg.reply_text(
            text="**You don't have any config first make the config then you'll able to report**\n\nUse /make_config",
            reply_to_message_id=msg.id,
            reply_markup=ReplyKeyboardRemove()
        )

    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    accounts = config.get("accounts", [])
    if len(accounts) < 5:
        return await msg.reply_text(
            text="**⚠️ Kam se kam 5 accounts config mein hone chahiye!**\n\nUse /make_config to add accounts.",
            reply_to_message_id=msg.id
        )

    # Check if already running
    if Path('report.txt').exists():
        return await msg.reply_text(
            text="**⚠️ Already One Process is Ongoing Please Wait Until it's Finished ⏳**",
            reply_to_message_id=msg.id
        )

    try:
        # Pehle crime message poocho
        crime_ask = await bot.ask(
            text="**📝 Crime Message likhein jo Telegram ko bhejna hai:**\n\n"
                 "Jaise:\n"
                 "• `This account is spreading scams and fraud`\n"
                 "• `This account is impersonating and doing illegal activities`\n"
                 "• `This account is sharing spam and fake links`\n\n"
                 "Ya aap directly number dal sakte ho template ke liye:\n"
                 "`1` - Spam/Scam\n"
                 "`2` - Impersonation\n"
                 "`3` - Copyright violation\n"
                 "`4` - Financial fraud\n"
                 "`5` - Violence\n"
                 "`6` - Child abuse\n"
                 "`7` - Pornography\n"
                 "`8` - Illegal drugs\n"
                 "`9` - Personal details leak",
            chat_id=msg.chat.id,
            filters=filters.text,
            timeout=120,
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        await bot.send_message(msg.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /report")
        return

    # Check if user gave number (template) or custom message
    crime_text = crime_ask.text.strip()
    if crime_text.isnumeric() and crime_text in CRIME_MESSAGES:
        crime_message = CRIME_MESSAGES[crime_text]
        await bot.send_message(
            chat_id=msg.chat.id,
            text=f"✅ Template selected: `{crime_message[:60]}...`"
        )
    else:
        crime_message = crime_text
        await bot.send_message(
            chat_id=msg.chat.id,
            text=f"✅ Custom crime message set: `{crime_message[:60]}...`"
        )

    try:
        no_of_reports = await bot.ask(
            text=Txt.SEND_NO_OF_REPORT_MSG.format(config['Target']),
            chat_id=msg.chat.id,
            filters=filters.text,
            timeout=300,
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        await bot.send_message(msg.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /report")
        return

    ms = await bot.send_message(
        chat_id=msg.chat.id,
        text=f"**⏳ Reporting in Progress...**\n\n"
             f"🎯 Target: @{config['Target']}\n"
             f"📝 Crime: {crime_message[:50]}...\n"
             f"👤 Accounts: {len(accounts)}\n"
             f"⏱️ Delay: 10 sec\n"
             f"🔄 Please wait...",
        reply_to_message_id=msg.id,
        reply_markup=ReplyKeyboardRemove()
    )
    
    if not str(no_of_reports.text).isnumeric():
        await msg.reply_text(text='**Please Enter Valid Integer Number !**\n\nTry Again :- /report')
        return

    reports_count = int(no_of_reports.text)
    
    max_allowed = 15
    if reports_count > max_allowed:
        await bot.send_message(
            chat_id=msg.chat.id,
            text=f"**⚠️ Maximum {max_allowed} reports allowed. {reports_count} ki jagah {max_allowed} set kiya.**"
        )
        reports_count = max_allowed

    total_reports = 0
    total_success = 0
    total_failed = 0
    
    rounds_needed = (reports_count + 4) // 5
    
    with open('report.txt', 'a') as log_file:
        log_file.write(f"=== Report Session Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log_file.write(f"Target: @{config['Target']} | Reason: {number} | Crime: {crime_message}\n")
        log_file.write(f"Accounts: {len(accounts)} | Max Reports: {reports_count}\n\n")

    for round_num in range(rounds_needed):
        remaining = reports_count - total_success
        if remaining <= 0:
            break
            
        await ms.edit_text(
            text=f"**⏳ Reporting in Progress...**\n\n"
                 f"🎯 Target: @{config['Target']}\n"
                 f"📝 Crime: {crime_message[:40]}...\n"
                 f"🔄 Round: {round_num + 1}/{rounds_needed}\n"
                 f"✅ Success: {total_success}\n"
                 f"❌ Failed: {total_failed}\n"
                 f"⏱️ Delay: 10 sec"
        )

        print(f"\n{'='*50}")
        print(f"📢 Round {round_num + 1}/{rounds_needed} | Crime: {crime_message}")
        print(f"{'='*50}")
        
        result, success = await Report_Round(number, crime_message)
        
        if success:
            with open('report.txt', 'a') as log_file:
                log_file.write(f"--- Round {round_num + 1} ---\n")
                log_file.write(result + "\n")
            
            total_success += min(5, remaining if remaining < 5 else 5)
            total_reports += min(5, remaining if remaining < 5 else 5)
        else:
            with open('report.txt', 'a') as log_file:
                log_file.write(f"--- Round {round_num + 1} FAILED ---\n")
                log_file.write(result + "\n")
            total_failed += 5

        # 10 sec delay between rounds
        if round_num < rounds_needed - 1 and total_success + total_failed < reports_count:
            print(f"⏳ 10 second delay before next round...")
            await asyncio.sleep(10)

    # Final status
    summary_text = (
        f"**✅ Reporting Complete!**\n\n"
        f"🎯 Target: @{config['Target']}\n"
        f"📝 Crime: `{crime_message[:60]}...`\n"
        f"📊 Total: {total_reports} reports\n"
        f"✅ Success: {total_success}\n"
        f"❌ Failed: {total_failed}\n"
        f"⏱️ Delay: 10 seconds"
    )
    
    await ms.edit_text(text=summary_text)

    with open('report.txt', 'a') as log_file:
        log_file.write(f"\n=== Report Session Ended at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log_file.write(f"Total: {total_reports} | Success: {total_success} | Failed: {total_failed}\n\n")

    await msg.reply_text(text=summary_text)
    
    if os.path.exists('report.txt'):
        await bot.send_document(
            chat_id=msg.chat.id,
            document='report.txt',
            reply_to_message_id=msg.id
        )
        os.remove('report.txt')


@Client.on_message(filters.private & filters.user(Config.OWNER) & filters.command('report'))
async def handle_report(bot: Client, cmd: Message):
    CHOICE = [
        [("1"), ("2")], [("3"), ("4")], 
        [("5"), ("6")], [("7"), ("8")], 
        [("9")]
    ]

    await bot.send_message(
        chat_id=cmd.from_user.id,
        text=Txt.REPORT_CHOICE,
        reply_to_message_id=cmd.id,
        reply_markup=ReplyKeyboardMarkup(CHOICE, resize_keyboard=True)
    )


@Client.on_message(filters.regex("1"))
async def one(bot, msg):
    await CHOICE_OPTION(bot, msg, 1)

@Client.on_message(filters.regex("2"))
async def two(bot, msg):
    await CHOICE_OPTION(bot, msg, 2)

@Client.on_message(filters.regex("3"))
async def three(bot, msg):
    await CHOICE_OPTION(bot, msg, 3)

@Client.on_message(filters.regex("4"))
async def four(bot, msg):
    await CHOICE_OPTION(bot, msg, 4)

@Client.on_message(filters.regex("5"))
async def five(bot, msg):
    await CHOICE_OPTION(bot, msg, 5)

@Client.on_message(filters.regex("6"))
async def six(bot, msg):
    await CHOICE_OPTION(bot, msg, 6)

@Client.on_message(filters.regex("7"))
async def seven(bot, msg):
    await CHOICE_OPTION(bot, msg, 7)

@Client.on_message(filters.regex("8"))
async def eight(bot, msg):
    await CHOICE_OPTION(bot, msg, 8)

@Client.on_message(filters.regex("9"))
async def nine(bot, msg):
    await CHOICE_OPTION(bot, msg, 9)
