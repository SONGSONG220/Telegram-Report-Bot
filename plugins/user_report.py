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

# Crime message templates
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


async def Report_Round(reason_number, crime_message, bot, chat_id, status_msg):
    """Ek round me saare accounts se report with live Telegram status update"""
    
    # 🛑 STOP CHECK
    if Path('stop.txt').exists():
        print("🛑 Stop signal detected! Skipping this round.")
        return ["🛑 Stopped by user", False]
    
    listofchoise = [
        'Report for child abuse', 'Report for copyrighted content', 
        'Report for impersonation', 'Report an irrelevant geogroup',
        'Report an illegal durg', 'Report for Violence', 
        'Report for offensive person detail', 'Reason for Pornography', 
        'Report for spam'
    ]
    message_text = listofchoise[int(reason_number) - 1]

    print(f"🚀 Starting report round | Reason: {message_text} | Crime: {crime_message[:50]}...")
    
    # Update live status
    await status_msg.edit_text(
        text=f"**⏳ Reporting in Progress...**\n\n"
             f"📤 Launching report script...\n"
             f"📝 Crime: {crime_message[:40]}...\n"
             f"⏱️ Please wait..."
    )
    
    # Run script with live output capture
    process = subprocess.Popen(
        ["python", "report.py", message_text, crime_message],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered for live output
    )

    # Read output line by line for live updates
    stdout_lines = []
    current_account = ""
    current_status = ""
    
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            line = line.strip()
            stdout_lines.append(line)
            print(f"📺 {line}")  # Console pe live dikhega
            
            # Extract account name and status for Telegram update
            if "Connected" in line:
                current_account = line.split(":")[0] if ":" in line else ""
                await status_msg.edit_text(
                    text=f"**⏳ Reporting...**\n\n"
                         f"🔄 {current_account}\n"
                         f"🔗 Connected to target ✅\n"
                         f"📤 Sending report..."
                )
            elif "SENDING" in line or "sending" in line.lower():
                await status_msg.edit_text(
                    text=f"**⏳ Reporting...**\n\n"
                         f"🔄 {current_account}\n"
                         f"📤 Sending report to Telegram..."
                )
            elif "SENT SUCCESSFULLY" in line or "sent successfully" in line.lower():
                await status_msg.edit_text(
                    text=f"**⏳ Reporting...**\n\n"
                         f"🔄 {current_account}\n"
                         f"✅ Report sent successfully!\n"
                         f"📝 Crime: {crime_message[:40]}...\n"
                         f"⏱️ Waiting 10 seconds..."
                )
    
    stderr = process.stderr.read()
    return_code = process.wait()

    if stderr:
        print(f"STDERR: {stderr}")

    stdout_full = "\n".join(stdout_lines)
    
    if return_code == 0:
        return [stdout_full, True]
    else:
        return [f"<b>Error Occurred!</b>\n\n<code>{stderr}</code>", False]


async def CHOICE_OPTION(bot, msg, number):
    """5 accounts se auto-report with live status on Telegram"""

    if not config_path.exists():
        return await msg.reply_text(
            text="**You don't have any config first make the config then you'll able to report**\n\nUse /make_config",
            reply_to_message_id=msg.id,
            reply_markup=ReplyKeyboardRemove()
        )

    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    accounts = config.get("accounts", [])
    if len(accounts) < 1:
        return await msg.reply_text(
            text="**⚠️ Kam se kam 1 account config mein hona chahiye!**",
            reply_to_message_id=msg.id
        )

    # 🛑 Purana stop.txt hatao
    if Path('stop.txt').exists():
        os.remove('stop.txt')

    if Path('report.txt').exists():
        return await msg.reply_text(
            text="**⚠️ Already One Process is Ongoing Please Wait ⏳**",
            reply_to_message_id=msg.id
        )

    try:
        crime_ask = await bot.ask(
            text="**📝 Crime Message likhein:**\n\n"
                 "Custom likho ya template number:\n"
                 "`1` - Spam/Scam\n`2` - Impersonation\n`3` - Copyright\n"
                 "`4` - Financial fraud\n`5` - Violence\n`6` - Child abuse\n"
                 "`7` - Pornography\n`8` - Illegal drugs\n`9` - Personal details",
            chat_id=msg.chat.id,
            filters=filters.text,
            timeout=120,
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        await bot.send_message(msg.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /report")
        return

    crime_text = crime_ask.text.strip()
    if crime_text.isnumeric() and crime_text in CRIME_MESSAGES:
        crime_message = CRIME_MESSAGES[crime_text]
        await bot.send_message(chat_id=msg.chat.id, text=f"✅ Template selected: `{crime_message[:60]}...`")
    else:
        crime_message = crime_text
        await bot.send_message(chat_id=msg.chat.id, text=f"✅ Custom crime message set")

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

    # Create live status message that will be updated
    status_msg = await bot.send_message(
        chat_id=msg.chat.id,
        text=f"**⏳ Starting Report Session...**",
        reply_to_message_id=msg.id
    )
    
    if not str(no_of_reports.text).isnumeric():
        await msg.reply_text(text='**Please Enter Valid Integer Number !**\n\nTry Again :- /report')
        return

    reports_count = int(no_of_reports.text)
    
    total_success = 0
    total_failed = 0
    accounts_count = len(accounts)
    rounds_needed = (reports_count + accounts_count - 1) // accounts_count
    
    with open('report.txt', 'a') as log_file:
        log_file.write(f"=== Report Session Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log_file.write(f"Target: @{config['Target']} | Reason: {number} | Crime: {crime_message}\n")
        log_file.write(f"Accounts: {accounts_count} | Total Reports: {reports_count}\n\n")

    for round_num in range(rounds_needed):
        # 🛑 STOP CHECK
        if Path('stop.txt').exists():
            await status_msg.edit_text(
                text=f"**🛑 STOPPED BY USER!**\n\n"
                     f"✅ Success: {total_success}\n"
                     f"❌ Failed: {total_failed}\n"
                     f"🛑 Stopped at Round {round_num + 1}"
            )
            print("🛑 User requested stop.")
            with open('report.txt', 'a') as log_file:
                log_file.write(f"\n=== STOPPED BY USER at Round {round_num + 1} ===\n")
            break
            
        remaining = reports_count - total_success
        if remaining <= 0:
            break
            
        # Live Telegram status
        await status_msg.edit_text(
            text=f"**⏳ Round {round_num + 1}/{rounds_needed}**\n\n"
                 f"🎯 Target: @{config['Target']}\n"
                 f"📝 Crime: {crime_message[:35]}...\n"
                 f"✅ Success: {total_success}\n"
                 f"❌ Failed: {total_failed}\n"
                 f"⏱️ Delay: 10 sec\n"
                 f"🛑 /stop to cancel"
        )

        print(f"\n{'='*50}")
        print(f"📢 Round {round_num + 1}/{rounds_needed} | Remaining: {remaining}")
        print(f"{'='*50}")
        
        if Path('stop.txt').exists():
            break
            
        result, success = await Report_Round(number, crime_message, bot, msg.chat.id, status_msg)
        
        if success:
            with open('report.txt', 'a') as log_file:
                log_file.write(f"--- Round {round_num + 1} ---\n")
                log_file.write(result + "\n")
            
            reports_this_round = min(accounts_count, remaining)
            total_success += reports_this_round
        else:
            with open('report.txt', 'a') as log_file:
                log_file.write(f"--- Round {round_num + 1} FAILED ---\n")
                log_file.write(result + "\n")
            total_failed += accounts_count

        # Live update after round
        await status_msg.edit_text(
            text=f"**⏳ Round {round_num + 1} Complete**\n\n"
                 f"🎯 Target: @{config['Target']}\n"
                 f"✅ Success: {total_success}\n"
                 f"❌ Failed: {total_failed}\n"
                 f"⏱️ Next round in 10 sec..."
        )

        if Path('stop.txt').exists():
            break

        if round_num < rounds_needed - 1 and total_success + total_failed < reports_count:
            print(f"⏳ 10 second delay before next round...")
            for sec in range(10, 0, -1):
                if Path('stop.txt').exists():
                    print("🛑 Stop during delay!")
                    break
                await asyncio.sleep(1)
            if Path('stop.txt').exists():
                break

    # Final status
    stopped = Path('stop.txt').exists()
    final_text = (
        f"{'🛑 **STOPPED!**' if stopped else '✅ **COMPLETE!**'}\n\n"
        f"🎯 Target: @{config['Target']}\n"
        f"📝 Crime: {crime_message[:50]}...\n"
        f"✅ Success: {total_success}\n"
        f"❌ Failed: {total_failed}\n"
        f"📊 Total Rounds: {round_num + 1}"
    )
    
    await status_msg.edit_text(text=final_text)

    with open('report.txt', 'a') as log_file:
        log_file.write(f"\n=== {'STOPPED' if stopped else 'COMPLETED'} at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log_file.write(f"Success: {total_success} | Failed: {total_failed}\n\n")

    await msg.reply_text(text=final_text)
    
    if os.path.exists('report.txt'):
        await bot.send_document(
            chat_id=msg.chat.id,
            document='report.txt',
            reply_to_message_id=msg.id
        )
        os.remove('report.txt')
    
    if os.path.exists('stop.txt'):
        os.remove('stop.txt')


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


# 🛑 STOP COMMAND
@Client.on_message(filters.private & filters.user(Config.OWNER) & filters.command('stop'))
async def stop_report(bot: Client, cmd: Message):
    """Stop the ongoing report process"""
    with open('stop.txt', 'w') as f:
        f.write('stop')
    await cmd.reply_text(
        text="**🛑 Stop signal sent!**\n\nReporting will stop after current account.\n\nUse /report to start again.",
        reply_to_message_id=cmd.id
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
