import re
import urllib.parse
import email_validator
import phonenumbers
from phonenumbers import phonenumberutil


from plate import Plate
plate = Plate()

from .logger import init_logger
logger = init_logger("utils.validation")

class InputValidator:
    def __init__(self, main_process="RU"):
        self.main_process = main_process

    @staticmethod
    def is_cyrillic(text, user_language):
        cyrillic_chars = [chr(i) for i in range(1072, 1106)] + [" ", "-"]
        for char in text.lower():
            if char not in cyrillic_chars:
                return plate("validation_use_cyrillic", user_language)
        return True

    @staticmethod
    def is_letter(text, user_language):
        for char in text.lower().replace(" ", "").replace("-", ""):
            if not char.isalpha():
                return plate("validation_use_letters", user_language)
        return True

    @staticmethod
    def is_phone(text, user_language, area="RU"):
        try:
            phone_number = phonenumbers.parse(text, area)
            if phonenumberutil.is_valid_number(phone_number):
                return True
            else:
                return plate("validation_invalid_phone", user_language)
        except phonenumbers.phonenumberutil.NumberParseException:
            return plate("validation_format_phone", user_language)

    @staticmethod
    def is_email(text, user_language):
        try:
            email_validator.validate_email(text)
            return True
        except email_validator.EmailNotValidError as e:
            return str(e)

    @staticmethod
    def is_date(text, user_language):
        digits = "".join([char for char in text if char.isdigit()])
        try:
            if 0 < int(digits[:2]) < 32 \
                    and 0 < int(digits[2:4]) < 13 \
                    and 1900 < int(digits[4:]) < 2050 \
                    and len(digits) == 8:
                return True
            else:
                return plate("validation_not_date", user_language)
        except Exception as err:
            logger.exception(err)
            return plate("validation_not_date", user_language)

    @staticmethod
    def is_url(text, user_language):
        url_regex = r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
        if re.match(url_regex, text):
            try:
                urllib.parse.urlparse(text)
                return True
            except ValueError:
                return plate("validation_format_url", user_language)
        else:
            return plate("validation_invalid_url", user_language)