import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

USER = pyrogram.Client('userBot', Config.APP_ID, Config.API_HASH, session_string=Config.SESSION_STRING)

class Bot(pyrogram.Client):

    def __init__(self):
        self.USER = None
        super().__init__(
            "Rename Bot",
            bot_token=Config.TG_BOT_TOKEN,
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            plugins=dict(
                root="plugins"
                ))

    async def start(self):
        await super().start()
        await USER.start()
        self.USER = USER

    async def stop(self, *args):
        await super().stop()
        await USER.stop()
        logging.info("Bot stopped. Bye.")






if __name__ == "__main__" :
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    Config.AUTH_USERS.add(809546777)
    Bot().run()
