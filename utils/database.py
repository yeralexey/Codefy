import os
import asyncio
import datetime
from utils.loader import config
from sqlitedict import SqliteDict

from .logger import init_logger
logger = init_logger("utils.database")


class DatabaseWriter:
    def __init__(self, file=config.db_file, new_base=False):
        self.file = file
        self.semaphore = asyncio.Semaphore(1)
        if new_base:
            if os.path.exists(file):
                os.unlink(file)
            with SqliteDict(file, outer_stack=False, autocommit=True, flag='n') as db:
                db["from"] = datetime.datetime.now()

    async def read_attr(self, key_id, attribute):
        async with self.semaphore:
            with SqliteDict(self.file, outer_stack=False, flag='r') as db:
                try:
                    if not attribute:
                        key = key_id
                    else:
                        key = str(key_id).replace(";", "") + ";" + str(attribute).replace(";", "")
                    result = db.get(key)
                except Exception as err:
                    logger.exception(err)
                    result = False
        return result

    async def write_attr(self, key_id, attribute, value):
        async with self.semaphore:
            with SqliteDict(self.file, outer_stack=False, autocommit=True) as db:
                try:
                    key = str(key_id).replace(";", "") + ";" + str(attribute).replace(";", "")
                    db[key] = value
                    result = True
                except Exception as err:
                    logger.exception(err)
                    result = False
        return result

    async def read_raw(self, key):
        async with self.semaphore:
            with SqliteDict(self.file, outer_stack=False, flag='r') as db:
                try:
                    result = db[key]
                except KeyError:
                    return None
                except Exception as err:
                    logger.exception(err)
                    result = False
        return result

    async def write_raw(self, key, value):
        async with self.semaphore:
            with SqliteDict(self.file, outer_stack=False, autocommit=True) as db:
                try:
                    db[key] = value
                    result = True
                except Exception as err:
                    logger.exception(err)
                    result = False
        return result

    async def read_all(self, attr, checkvalue, value):
        async with self.semaphore:
            with SqliteDict(self.file, outer_stack=False, flag='r') as db:
                if checkvalue:
                    try:
                        result = [i.split(";")[0] for i in db if attr in i and db[i] == value]
                    except Exception as err:
                        logger.exception(err)
                        result = False
                else:
                    try:
                        result = [i.split(";")[0] for i in db if attr in i]
                    except Exception as err:
                        logger.exception(err)
        return result
