from utils.loader import config
from .validation import InputValidator
from .database import DatabaseWriter
from .system import SystemController
from .googlejobs import GoogleWorker
from .keyboard import ikb


from .logger import init_logger
logger = init_logger('main')

from plate import Plate
plate = Plate()

vd = InputValidator()
db = DatabaseWriter()
cr = SystemController(config.name)
keyboard = ikb

try:
    gw = GoogleWorker(config.google_credentials, config.main_sheet)
except ValueError:
    gw = None
