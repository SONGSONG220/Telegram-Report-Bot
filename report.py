import sys
import asyncio
import json
import logging
from pyrogram import Client
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import *

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# --- REASON MAPPING ---
def get_reason(text):
    """
    Yeh function English text ko Telegram ke RAW API format mein badalta hai.
    """
    reasons = {
        "Report for child abuse": InputReportReasonChildAbuse(),
        "Report for impersonation": InputReportReasonFake(),
        "Report for copyrighted content": InputReportReasonCopyright(),
        "Report an irrelevant geogroup": InputReportReasonGeoIrrelevant(),
        "Reason for Pornography": InputReportReasonPornography(),
        "Report an illegal durg": InputReportReasonIllegalDrugs(),
        "Report for offensive person detail": InputReportReasonPersonalDetails(),
        "Report for spam": InputReportReasonSpam(),
        "Report for Violence": InputReportReasonViolence()
    }
    return reasons.get(text)

# --- MAIN ENGINE ---
async def main(full_input):
    """
    Yeh function har account se login karke target ko strike karega.
    """
    # 1. Config file load karna
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Fatal Error: Config file nahi mili ya kharab hai! ({e})")
        return

    # 2. Input String ko Todna (Reason vs Evidence)
    if "\n\nEvidence/Details:\n" in full_input:
        reason_text, crime_details = full_input.split("\n\nEvidence/Details:\n", 1)
    else:
        reason_text = full_input
        crime_details = "Manual report filed via automated system."

    # 3. Reason Check
    report_reason = get_reason(reason_text)
    if not report_reason:
        print(f"Error: Invalid Reason Provided -> {reason_text}")
        return

    target = config.get('Target')
    accounts = config.get("accounts", [])

    if not accounts:
        print("Error: Config mein koi accounts nahi mile!")
        return

    print(f"Starting Reports on: @{target}")
    print(f"Reason: {reason_text}")

    # 4. Accounts Loop (Har account se strike)
    for account in accounts:
        session = account.get("Session_String")
        name = account.get('OwnerName', 'User')

        if not session:
            print(f"Skipping {name}: No Session String found.")
            continue

        # in_memory=True taaki Pydroid ya Hosting par faltu .session files na bane
        async with Client(name="ReportSession", session_string=session, in_memory=True, device_model="ReportBotV2") as app:
            try:
                # Target ki ID aur Access Hash nikalna
                peer = await app.resolve_peer(target)
                
                # Peer Type Identify karna (Channel, User, ya Chat)
                if hasattr(peer, 'channel_id'):
                    input_peer = InputPeerChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)
                elif hasattr(peer, 'user_id'):
                    input_peer = InputPeerUser(user_id=peer.user_id, access_hash=peer.access_hash)
                elif hasattr(peer, 'chat_id'):
                    input_peer = InputPeerChat(chat_id=peer.chat_id)
                else:
                    print(f"Unknown Peer Type for {target}")
                    continue

                # --- THE STRIKE ---
                # Crime details 'message' parameter mein jayengi jo Telegram Admin dekhega
                await app.invoke(
                    ReportPeer(
                        peer=input_peer, 
                        reason=report_reason, 
                        message=crime_details
                    )
                )
                print(f"✅ Success: Reported by {name}")
                
                # Rate limit se bachne ke liye chhota sa gap
                await asyncio.sleep(1)

            except Exception as e:
                print(f"❌ Failed for {name}: {str(e)}")

# --- ENTRY POINT ---
if __name__ == "__main__":
    # Check karna ki argument bhej gaya hai ya nahi
    if len(sys.argv) < 2:
        print("Usage: python report.py <combined_reason_and_details>")
        sys.exit(1)

    # Pura input uthana (Spaces ke sath)
    combined_input = sys.argv[1]
    asyncio.run(main(combined_input))
    
