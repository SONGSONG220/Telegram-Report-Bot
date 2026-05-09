import sys
from pyrogram import Client
import asyncio
import json
import time
import random
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
    """
    crime_message: Yeh message Telegram ko bheja jayega report ke saath
    """
    try:
        config = json.load(open("config.json"))
    except FileNotFoundError:
        print("Error: config.json not found!")
        return 0, 0
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json!")
        return 0, 0

    resportreason = get_reason(reason_text)
    if resportreason is None:
        print(f"Error: Invalid reason provided: {reason_text}")
        return 0, 0

    target = target_override or config.get('Target')
    if not target:
        print("Error: 'Target' not specified in config.json")
        return 0, 0

    accounts = config.get("accounts", [])
    if not accounts:
        print("Error: No accounts found in config.json")
        return 0, 0

    success_count = 0
    fail_count = 0

    for idx, account in enumerate(accounts):
        string = account.get("Session_String")
        Name = account.get('OwnerName', f'Account{idx+1}')
        
        if not string:
            print(f"❌ {Name}: No Session_String found")
            fail_count += 1
            continue
        
        try:
            async with Client(name=f"Session_{idx}_{int(time.time())}", session_string=string, in_memory=True) as app:
                peer = await app.resolve_peer(target)
                
                # Handle different peer types
                if hasattr(peer, 'channel_id'):
                    input_peer = InputPeerChannel(
                        channel_id=peer.channel_id,
                        access_hash=peer.access_hash
                    )
                elif hasattr(peer, 'user_id'):
                    input_peer = InputPeerUser(
                        user_id=peer.user_id,
                        access_hash=peer.access_hash
                    )
                elif hasattr(peer, 'chat_id'):
                    input_peer = InputPeerChat(chat_id=peer.chat_id)
                else:
                    print(f"❌ {Name}: Unknown peer type for {target}")
                    fail_count += 1
                    continue
                
                report_peer = ReportPeer(
                    peer=input_peer,
                    reason=resportreason,
                    message=crime_message  # 🆕 Custom crime message bhej raha hai Telegram ko
                )
                
                result = await app.invoke(report_peer)
                print(f"✅ {Name}: Report sent successfully!")
                print(f"   📝 Crime Message: {crime_message}")
                print(f"   🎯 Target: @{target}")
                success_count += 1
                
                # ⚡ 10 SECOND DELAY ⚡
                if idx < len(accounts) - 1:
                    print(f"⏳ Waiting 10 seconds before next account...")
                    await asyncio.sleep(10)
                 
        except Exception as e:
            print(f"❌ {Name}: Error - {e}")
            fail_count += 1
            if idx < len(accounts) - 1:
                await asyncio.sleep(5)
    
    summary = f"\n📊 Report Summary: ✅ {success_count} Success | ❌ {fail_count} Failed | 🎯 @{target} | 📝 {crime_message[:50]}..."
    print(summary)
    return success_count, fail_count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python report.py <reason> [crime_message] [target_username]")
        print("\nAvailable reasons:")
        print("  - Report for child abuse")
        print("  - Report for impersonation")
        print("  - Report for copyrighted content")
        print("  - Report an irrelevant geogroup")
        print("  - Reason for Pornography")
        print("  - Report an illegal durg")
        print("  - Report for offensive person detail")
        print("  - Report for spam")
        print("  - Report for Violence")
        sys.exit(1)

    input_string = sys.argv[1]
    crime_message = sys.argv[2] if len(sys.argv) > 2 else "This account is violating Telegram policies."
    target_override = sys.argv[3] if len(sys.argv) > 3 else None
    asyncio.run(main(input_string, crime_message, target_override))
