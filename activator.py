# pip install tgcrypto uvloop pyrogram pyromod plate sqlitedict oauth2client google-api-python-client email-validator phonenumbers

from maindata import config

from pyrogram import Client

api_id = "<PASTE_YOUR_DATA_HERE>"  # int awaited
api_hash = "000<PASTE_YOUR_DATA_HERE>6c9"
bot_token = "59<PASTE_YOUR_DATA_HERE>vk"

app = Client(f"{config.name}",
             api_id=api_id,
             api_hash=api_hash,
             bot_token=bot_token,
             workdir=config.workdir)

app.start()
app.stop()
