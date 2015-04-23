from blinker import signal
from watchtower.models import BlacklistEntry
import re

class Detector:
    def detect(self, message):
        raise NotImplemented()

class BlacklistDetector(Detector):
    name = "blacklisting"
    def detect(self, message):
        cscore = 0
        patterns = list(map(lambda k: (k.pattern, k.weight), BlacklistEntry().select()))
        for pattern, weight in patterns:
            if re.match(pattern, message) is not None:
                cscore += weight
        return cscore

detectors = [BlacklistDetector()]

pubmsg = signal("public-message")
@pubmsg.connect
def handle_messages(message, user, target, text):
    score = 0
    triggered = set()
    for detector in detectors:
        cscore = detector.detect(text)
        if cscore:
            triggered.add(detector.name)
            score += cscore

    if score > 0:
        signal("detectors-triggered").send(message, user=user, target=target, text=text, triggered=triggered, score=score)

