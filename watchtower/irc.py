from .config import config
from .models import Channel

import asyncirc.plugins.addressed
import asyncirc.plugins.nickserv
import asyncirc.plugins.tracking

from asyncirc import irc

import inspect
import logging
import shlex

server_config = config["irc-server"]
user_config = config["irc-user"]
auth_config = config["irc-auth"]

logger = logging.getLogger("irc")

bot = irc.connect(server_config["host"], int(server_config["port"]), use_ssl=bool(server_config["ssl"]))
bot.register(user_config["nick"], user_config["ident"], user_config["realname"],
             password=auth_config["password"])

registry = asyncirc.plugins.tracking.registry

def join_channel(channel):
    bot.join(channel)
    if Channel.get(Channel.name == channel) is not None:
        return False, "The channel is already in the configuration."
    Channel.create(name=channel, config="{}")
    return True, "Channel added with default configuration."

def leave_channel(channel):
    bot.part(channel)
    if Channel.get(Channel.name == channel) is None:
        return False, "The channel is not in the configuration."
    Channel.delete().where(Channel.name == channel).execute()
    return True, "Channel removed from configuration."

def channel_membership(user):
    if user not in registry.users:
        return False, "I don't know anything about {}.".format(user)
    return True, "{} is on {}.".format(user, ", ".join(list(registry.users[user].channels)))

channels = set([i.name for i in Channel.select()]) | {config["irc-channels"]["monitor"]}
@bot.on("nickserv-auth-success")
def autojoin(message):
    logger.warn("NickServ auth complete")
    bot.join(config["irc-channels"]["monitor"])
    for channel in channels:
        bot.join(channel)

channels_synced = set()
@bot.on("sync-done")
def sync_done(channel):
    channels_synced.add(channel)
    if channels_synced == channels:
        bot.say(config["irc-channels"]["monitor"], "Sync to {} channel(s) complete.".format(len(channels_synced)))

commands = {"join": join_channel, "part": leave_channel, "membership": channel_membership}

@bot.on("addressed")
def dispatch_command(message, user, target, text):
    split = shlex.split(text)
    command, args = split[0], split[1:]
    if len(args) != len(inspect.getargspec(commands[command])[0]):
        bot.say(target, "Wrong number of arguments.")
        return
    success, message = commands[command](*args)
    if success:
        bot.say(target, "Operation successful. {}".format(message))
    else:
        bot.say(target, "Operation failed. {}".format(message))
