from blinker import signal
from . import config

def handle_triggered(message, user, target, text, triggered, score):
    message.client.say(config.config["irc-channels"]["monitor"], "{} triggered {} with score {}".format(user.nick, ", ".join(triggered), score))

signal("detectors-triggered").connect(handle_triggered)
