from blinker import signal

class Detector:
    def detect(self, message):
        raise NotImplemented()

class SpamDetector:
    def detect(self, message):
        if "spammy spam" in message:
            return 0.5
        else:
            return 0

detectors = [SpamDetector()]

pubmsg = signal("public-message")
@pubmsg.connect
def handle_messages(message, user, target, text):
    score = 0
    for detector in detectors:
        score += detector.detect(text)
    if score > 0:
        signal("detectors-triggered").send(message, user=user, target=target, text=text, score=score)
