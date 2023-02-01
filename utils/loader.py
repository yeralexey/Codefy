from pyrogram import Client
import json
import pickle
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
fernet = Scrypt(salt=bytes(612), length=32, n=2**14, r=8, p=1).derive("fernet".encode())
fernet = base64.urlsafe_b64encode(fernet)
fernet = Fernet(fernet)

workdir = "maindata/"


class Config:

    def __init__(self):
        print("creating config")
        self.workdir = workdir

        self.name = input("project name :")
        self.owner = int(input("owner telegram id :"))
        api_id = int(input("api id :"))
        api_hash = input("api hash :")
        bot_token = input("bot token :")
        self.main_sheet = input("google sheet :")

        app = Client(f"{self.name}",
                     api_id=api_id,
                     api_hash=api_hash,
                     bot_token=bot_token,
                     workdir=workdir)
        app.start()
        app.stop()

        self.main_log = f"{workdir}{self.name}.log"
        self.mail_logs = "maillogs/"
        self.db_file = f'{workdir}main.db'
        self.csv_file = f'{workdir}main.csv'
        with open(f"{workdir}googlecredentials.json", "r") as file:
            self.google_credentials = json.load(file)
        self.admins = [self.owner]

try:
    with open(f"{workdir}temp.session", "rb") as file:
        data = file.read()
    data = fernet.decrypt(data)
    config = pickle.loads(data)

except FileNotFoundError:
    config = Config()
    data = pickle.dumps(config)
    data = fernet.encrypt(data)
    with open(f"{workdir}temp.session", "wb") as file:
        file.write(data)
