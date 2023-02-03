from utils import db, plate
from typing import Union, Any
import datetime

from utils.logger import init_logger
logger = init_logger("entities.userdata")

class User:
    """
    Represents a user and provides methods for interacting with the user's data. Please, make sure that description
    for representing of each attribute you add is made in /locales, otherwise data will not be shown by /mydata
    command, check create_user_data method below.
    """
    user_dict = {}
    default_language = "ru_RU"

    def __init__(self, user_id: int):
        self.user_index = None
        self.user_id = user_id
        self.user_name = None
        self.lastname = None
        self.name = None
        self.patronymic = None
        self.email = None
        self.phone = None
        self.passport = None
        self.regaddress = None
        self.gender = None
        self.chosen_language = None
        self.join_date = None
        self.last_act = None
        self.is_active = None
        self.is_sent = None

    async def get_attribute(self, attribute: str, setit=True) -> Union[Any, bool]:
        value = await db.read_attr(self.user_id, attribute)
        if setit:
            setattr(self, attribute, value)
        return value

    async def set_attribute(self, attribute: str, value) -> bool:
        if "_" not in attribute:
            setattr(self, "is_sent", False)
            await db.write_attr(self.user_id, "is_sent", False)
        setattr(self, attribute, value)
        result = await db.write_attr(self.user_id, attribute, value)
        if not result:
            return False
        return True

    async def act(self):
        result = await self.set_attribute("last_act", str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return result

    async def load_attributes(self) -> bool:
        for attr in self.__dict__.keys():
            try:
                await self.get_attribute(attr)
            except Exception as err:
                logger.exception(err)
                return False
        return True

    async def dump_attributes(self) -> bool:
        for attr, value in self.__dict__.items():
            result = await self.set_attribute(attr, value)
            if not result:
                return False
        return True

    async def create_user_data(self, current_step: str = None, technical: bool = False) -> Union[str, bool]:
        result = await self.load_attributes()
        if not result:
            return False
        data = ""
        tag_current_begin = "<u>**"
        tag_current_end = "**</u>"
        tag_usual = "`"
        attr_lst = self.__dict__.keys()
        if technical is False:
            attr_lst = [i for i in attr_lst if "_" not in i]
        for attr in attr_lst:
            value = getattr(self, attr)
            if current_step == attr:
                data += f"{tag_current_begin}{plate(f'userdata_{attr}', self.chosen_language)}:{tag_current_end} "
            else:
                data += f"{tag_usual}{plate(f'userdata_{attr}', self.chosen_language)}:{tag_usual} "
            data += f'{"no data" if value is None else value}\n'
        return data

    async def dict_dismiss(self):
        try:
            result = User.user_dict.pop(self.user_id)
        except KeyError:
            result = False
        return result

    @classmethod
    async def get_user(cls, user_id: int, user_name=None, set_active=False) -> "User":
        user = cls.user_dict.setdefault(user_id, User(user_id))
        await user.act()
        if user.chosen_language is None:
            await user.get_attribute("chosen_language")
            if user.chosen_language is None:
                await user.set_attribute("user_id", user_id)
                await user.set_attribute("user_name", user_name)
                await user.set_attribute("chosen_language", cls.default_language)
                await user.set_attribute("join_date", str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                index = await User.main_index(get_next=True)
                await user.set_attribute("user_index", index)
                await user.set_attribute("is_active", False)
                await user.set_attribute("is_sent", False)
        if set_active is True:
            await user.set_attribute("is_active", True)
        return user

    @classmethod
    async def get_attribute_list(cls):
        obj = User(1)
        result = [i for i in obj.__dict__.keys()]
        return result

    @staticmethod
    async def get_users(attribute="user_id", checkvalue=False, value=None):
        result = await db.read_all(attribute, checkvalue, value)
        return result

    @staticmethod
    async def main_index(get_next=False, value=None):
        if value is not None:
            if isinstance(value, int):
                return await db.write_raw("index", value)
        result = await db.read_raw("index") or 1
        if get_next:
            result += 1
            await db.write_raw("index", result)
        return result
