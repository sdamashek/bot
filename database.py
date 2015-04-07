from config import config
from peewee import *

class UnknownDriverException(Exception): pass

dbconfig = config["database"]

if dbconfig["driver"] == "sqlite":
    db = SqliteDatabase(dbconfig["database"])
else:
    raise UnknownDriverException("Unknown database driver {}.".format(dbconfig["driver"]))
