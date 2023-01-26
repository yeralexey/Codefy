from maindata import config
from .validation import InputValidator
from .database import DatabaseWriter
from .system import SystemController
from .googlejobs import GoogleWorker


vd = InputValidator()
db = DatabaseWriter()
cr = SystemController(config.name)
gw = GoogleWorker(config.google_credentials, config.main_sheet)
