from .database import db
from peewee import *


class BaseModel(Model):

    class Meta:
        database = db


class Channel(BaseModel):
    name = TextField()
    config = TextField()  # i am making a terrible mistake (JSON serialized)


class Permission(BaseModel):
    account = TextField()
    permission = TextField()
    channel = TextField(default="*")


class BlacklistEntry(BaseModel):
    weight = IntegerField(default=5)
    pattern = TextField()
    reason = TextField(default="no reason")
