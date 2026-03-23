from pyromod import Client
from pyrogram import __version__
from pyrogram.raw.all import layer
from info import Config
import logging
from datetime import datetime
import logging.config, os
from pytz import timezone
from aiohttp import web
import pyromod

# Logging setup
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes([web.get("/", lambda r: web.Response(text="Hello"))])
    return web_app

class Bot (Client):

    def __init__(self):
        super().__init__(
            name="ReportBot",
            in_memory=True,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins={'root': 'plugins'}
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, Config.PORT).start()
        logging.info(f"✅ {me.first_name} started on {me.username}. ✅")

        # FIX: Multiple Owners ko message bhejne ka sahi tarika
        if isinstance(Config.OWNER, list):
            for admin_id in Config.OWNER:
                try:
                    await self.send_message(admin_id, f"**__{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")
                except Exception as e:
                    logging.warning(f"Could not send message to {admin_id}: {e}")
        else:
            await self.send_message(Config.OWNER, f"**__{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped ⛔")

bot = Bot()
bot.run()
