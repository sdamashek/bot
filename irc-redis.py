from asyncirc import irc
from config import config

import asyncirc.plugins.nickserv

server = config["irc-server"]
auth = config["irc-auth"]
user = config["irc-user"]

bot = irc.connect(server["host"], server["port"], bool(server["ssl"]))

if auth["method"] == "password":
    bot.register(user["nick"], user["ident"], user["realname"], password=auth["password"])

    @bot.on("nickserv-auth-success")
    def auth_handler(message):
        bot.join(config["irc-channels"]["monitor"])

else:
    raise Exception("Unsupported authentication method")


