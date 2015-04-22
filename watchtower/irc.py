from .config import config
from .models import Channel, Permission

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

# TODO refactor into a capabilities plugin
bot.writeln("CAP REQ :account-notify extended-join")
bot.caps = bot.caps | {"extended-join"}
bot.writeln("CAP END")

if auth_config["method"] == "password":
    password = auth_config["password"]
elif auth_config["method"] == "null":
    password = None

bot.register(user_config["nick"], user_config["ident"], user_config["realname"], password=password)

registry = asyncirc.plugins.tracking.registry
channels = set([i.name for i in Channel.select()]) | {config["irc-channels"]["monitor"]}
@bot.on("nickserv-auth-success" if auth_config["method"] != "null" else "irc-001")
def autojoin(message):
    logger.info("Authentication complete.")
    bot.join(config["irc-channels"]["monitor"])
    for channel in channels:
        bot.join(channel)

channels_synced = set()
sync_notified = [False] # FIXME :(
@bot.on("sync-done")
def sync_done(channel):
    channels_synced.add(channel)
    if channels_synced == channels and not sync_notified[0]:
        sync_notified[0] = True
        bot.say(config["irc-channels"]["monitor"], "Sync to {} channel(s) complete.".format(len(channels_synced)))

commands = {}
def command(name, perm={"default"}, extra=[]):
    def decorate(f):
        commands[name] = (f, perm, extra)
        return f
    return decorate

def test_permissions(user, perm):
    account = asyncirc.plugins.tracking.get_user(user.hostmask).account
    plist = set(map(lambda k: k.permission, Permission.select().where(Permission.account == account))) | {"default"}
    return plist & perm != set()

def get_args(message, user, target, text, private=False):
    extra_args = {"account": asyncirc.plugins.tracking.get_user(user.hostmask).account,
                  "user": asyncirc.plugins.tracking.get_user(user.hostmask),
                  "private": private,
                  "message": message}
    return extra_args

def dispatch_command(message, user, reply_to, text):
    split = shlex.split(text)
    command, args = split[0], split[1:]
    func, perm, extra = commands[command]
    if not test_permissions(user, perm):
        bot.say(reply_to, "You do not have any of the required permissions.")
        return

    argspec = inspect.getfullargspec(func)
    min_args = len(argspec.args) - len(extra)
    if argspec.varargs is None:
        if len(args) != min_args:
            bot.say(target, "Wrong number of arguments. There must be exactly {}.".format(min_args))
            return
    else:
        if len(args) < min_args:
            bot.say(target, "Not enough arguments. There must be at least {}.".format(min_args))
            return

    extra_args = get_args(message, user, reply_to, text, False)
    args = [extra_args[a] for a in extra] + args

    success, message = func(*args)
    if success is True:
        bot.say(reply_to, "Operation successful. {}".format(message))
    elif success is False:
        bot.say(reply_to, "Operation failed. {}".format(message))
    elif success is None:
        bot.say(reply_to, message)

@bot.on("addressed")
def command_received(message, user, target, text):
    dispatch_command(message, user, target, text)

@bot.on("private-message")
def private_received(message, user, target, text):
    dispatch_command(message, user, user.nick, text)

@command("join", {"dev", "admin"})
def join_channel(channel):
    bot.join(channel)
    if list(Channel.select().where(Channel.name == channel)) != []:
        return False, "The channel is already in the configuration."
    Channel.create(name=channel, config="{}")
    return True, "Channel added with default configuration."

@command("part", {"dev", "admin"})
def leave_channel(channel):
    bot.part(channel)
    if list(Channel.select().where(Channel.name == channel)) == []:
        return False, "The channel is not in the configuration."
    Channel.delete().where(Channel.name == channel).execute()
    return True, "Channel removed from configuration."

@command("membership", {"dev", "analyst"}, ["private"])
def channel_membership(is_private, user):
    if user not in registry.users:
        return False, "I don't know anything about {}.".format(user)

    channels = sorted(list(registry.users[user].channels))
    secret_channels = {c for c in channels if "s" in get_channel(c).mode}
    if not channels:
        return None, "{} is in no channels that I know of.".format(user)
    if is_private:
        return None, "{} is on {}.".format(user, ", ".join(channels))
    else:
        nonsecret = [c for c in channels if c not in secret_channels]
        if not nonsecret:
            return None, "{} is on {} channels.".format(len(channels))
        elif not secret:
            return None, "{} is on {}.".format(user, ", ".join(channels))
        else:
            return None, "{} is on {}, and {} additional channels.".format(user, ", ".join(channels), len(secret_channels))

@command("channel", {"dev", "analyst"})
def channel_info(channel):
    if channel not in registry.channels:
        return False, "I don't know anything about {}".format(channel)
    channel_obj = asyncirc.plugins.tracking.get_channel(channel)
    return None, "{} has {} users and modes {} set.".format(channel, len(list(channel_obj.users)), channel_obj.mode)

@command("unsynced", {"dev"}, ["private"])
def unsynced(private):
    if not private:
        return False, "Please run this command in a PM."
    unsynced_channels = channels - channels_synced
    if len(unsynced_channels) == 0:
        return None, "There are no unsynced channels."
    return None, ", ".join(sorted(list(un)))

@command("help", {"default"}, ["account"])
def help(account):
    perms = set(map(lambda k: k.permission, Permission.select().where(Permission.account == account))) | {"default"}
    allowed = sorted([commands[command][1] for command in commands if commands[command][1] & perms != set()])
    return None, "Commands you can use: {}".format(", ".join(allowed))
