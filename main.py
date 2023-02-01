from utils.loader import config

import asyncio
from asyncio import exceptions
import datetime

from utils import gw, cr, db, vd
from entities import User, Interview

from pyrogram import Client, filters
from pyrogram.enums import ChatAction

import pyromod
from pyromod import listen
from pyromod.helpers import ikb

from utils.logger import init_logger
logger = init_logger('main')

from plate import Plate
plate = Plate()

if __name__ == '__main__':
    logger.info("app started")
    plugins = dict(root="plugins")
    Client(config.name, workdir=config.workdir, plugins=plugins).run()
