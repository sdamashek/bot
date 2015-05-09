from .config import config
from peewee import *


class UnknownDriverException(Exception):
    pass

dbconfig = config["database"]

if dbconfig["driver"] == "sqlite":
    db = SqliteDatabase(dbconfig["database"])
elif dbconfig["driver"] == "mysql":
    db = MySQLDatabase(dbconfig["database"], host=dbconfig["host"],
                       port=dbconfig["port"] if "port" in dbconfig else 3306, user=dbconfig["user"],
                       password=dbconfig["password"])
else:
    raise UnknownDriverException("Unknown database driver {}.".format(dbconfig["driver"]))
