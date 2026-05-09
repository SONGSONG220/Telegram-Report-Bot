import sys
from pyrogram import Client
import asyncio
import json
import time
from pathlib import Path
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import *


def get_reason(text):
    reasons = {
        "Report for child abuse": InputReportReasonChildAbuse(),
        "Report for impersonation": InputReportReasonFake(),
        "Report for copyrighted content": InputReportReasonCopyright(),
        "Report an irrelevant geogroup": InputReportReasonGeoIrrelevant(),
        "Reason for Pornography": InputReportReasonPornography(),
        "Report for an illegal durg": InputReportReasonIllegalDrugs(),
        "Report for offensive person detail": InputReportReasonPersonalDetails(),
        "Report for spam": InputReportReasonSpam(),
        "Report for Violence": InputReportReasonViolence(),
    }
    return reasons.get(text)


async def main(reason_text, crime_message="This account is violating Telegram policies.", target_override=None):
    try:
        config = json.load(open("config.json"))
    except FileNotFoundError:
        print("❌ Error: config.json not found!")
        return 0, 0
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in config.json!")
        return 0, 0

    resportreason = get_reason(reason_text)
    if resportreason is None:
        print(f"❌ Error: Invalid reason provided: {reason_text}")
        return 0, 0

    target = target_override or config.get('Target')
    if not target:
        print("❌ Error: 'Target' not specified in config.json")
        return 0, 0

    accounts = config.get("accounts", [])
    if not accounts:
        print("❌ Error: No accounts found in config.json")
        return 0, 0

    print(f"\n{'='*60}")
    print(f"📢 REPORT SESSION STARTED")
    print(f"{'='*60}")
    print(f"🎯 Target        : @{target}")
    print(f"📝 Crime Message : {crime_message}")
    print(f"👤 Total Accounts: {len(accounts)}")
    print(f"⏱️ Delay         : 10 seconds")
    print(f"{'='*60}\n")

    success_count = 0
    fail_count = 0

    for idx, account in enumerate(accounts):
        # 🛑 STOP CHECK
        if Path('stop.txt').exists():
            print(f"\n🛑 STOP SIGNAL DETECTED! Stopping at Account {idx+1}")
            break

        string = account.get("Session_String")
        Name = account.get('OwnerName', f'Account{idx+1}')
        
        if not string:
            print(f"❌ [{idx+1}/{len(accounts)}] {Name}: ⛔ No Session_String found")
            fail_count += 1
            continue
        
        try:
            async with Client(name=f"Session_{idx}_{int(time.time())}", session_string=string, in_memory=True) as app:
                print(f"🔄 [{idx+1}/{len(accounts)}] {Name}: Connecting...", end=" ", flush=True)
                
                peer = await app.resolve_peer(target)
                
                if hasattr(peer, 'channel_id'):
                    input_peer = InputPeerChannel(
                        channel_id=peer.channel_id,
                        access_hash=peer.access_hash
                    )
                    peer_type = "Channel/Group"
                elif hasattr(peer, 'user_id'):
                    input_peer = InputPeerUser(
                        user_id=peer.user_id,
                        access_hash=peer.access_hash
                    )
                    peer_type = "User"
                elif hasattr(peer, 'chat_id'):
                    input_peer = InputPeerChat(chat_id=peer.chat_id)
                    peer_type = "Chat"
                else:
                    print(f"\n❌ [{idx+1}/{len(accounts)}] {Name}: Unknown peer type for @{target}")
                    fail_count += 1
                    continue
                
                # 🛑 STOP CHECK before report
                if Path('stop.txt').exists():
                    print(f"\n🛑 STOP SIGNAL DETECTED!")
                    break
                
                print(f"✅ Connected | Type: {peer_type}")
                
                report_peer = ReportPeer(
                    peer=input_peer,
                    reason=resportreason,
                    message=crime_message
                )
                
                print(f"📤 [{idx+1}/{len(accounts)}] {Name}: Sending report...", end=" ", flush=True)
                
                result = await app.invoke(report_peer)
                print(f"✅ REPORT SENT SUCCESSFULLY ✅")
                print(f"   📝 Crime: {crime_message[:60]}...")
                print(f"   🎯 Target: @{target}")
                print(f"   {'─'*50}")
                success_count += 1
                
                # 10 sec delay between accounts
                if idx < len(accounts) - 1:
                    if Path('stop.txt').exists():
                        print(f"🛑 Stop signal detected! Skipping delay.")
                        break
                    print(f"⏳ Waiting 10 seconds before next account...")
                    for sec in range(10, 0, -1):
                        if Path('stop.txt').exists():
                            print(f"\n🛑 Stop signal detected during delay!")
                            break
                        print(f"   ⏱️ {sec} seconds remaining...", end="\r", flush=True)
                        await asyncio.sleep(1)
                    print(f"   ⏱️ 0 seconds remaining...   ")
                    print()
                 
        except Exception as e:
            print(f"\n❌ [{idx+1}/{len(accounts)}] {Name}: ERROR - {e}")
            print(f"   {'─'*50}")
            fail_count += 1
            if idx < len(accounts) - 1:
                await asyncio.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"📊 REPORT SESSION COMPLETED")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed : {fail_count}")
    print(f"🎯 Target : @{target}")
    print(f"{'='*60}\n")
    return success_count, fail_count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📋 Usage: python report.py <reason> [crime_message] [target_username]")
        print("\n📌 Available reasons:")
        print("  1. Report for child abuse")
        print("  2. Report for impersonation")
        print("  3. Report for copyrighted content")
        print("  4. Report an irrelevant geogroup")
        print("  5. Report for an illegal durg")
        print("  6. Report for Violence")
        print("  7. Report for offensive person detail")
        print("  8. Reason for Pornography")
        print("  9. Report for spam")
        sys.exit(1)

    input_string = sys.argv[1]
    crime_message = sys.argv[2] if len(sys.argv) > 2 else "This account is violating Telegram policies."
    target_override = sys.argv[3] if len(sys.argv) > 3 else None
    asyncio.run(main(input_string, crime_message, target_override))
