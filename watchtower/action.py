from blinker import signal
from . import config

def handle_triggered(message, user, target, text, score):
    pass

signal("detectors-triggered").connect(handle_triggered)
