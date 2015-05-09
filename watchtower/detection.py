from blinker import signal
from watchtower.detector import detectors
from watchtower.detectors import *


pubmsg = signal("public-message")


@pubmsg.connect
def handle_messages(message, user, target, text):

    score = 0
    triggered = set()
    for d in detectors:
        cscore = detectors[d](text)
        if cscore:
            triggered.add(d)
            score += cscore

    if score > 0:
        signal("detectors-triggered").send(message, user=user, target=target, text=text, triggered=triggered, score=score)
