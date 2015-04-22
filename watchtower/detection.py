from blinker import signal

class Detector:
    def detect(self, message):
        raise NotImplemented()

class SpamDetector(Detector):
    name = "spammy spam"
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
    triggered = set()
    for detector in detectors:
        cscore += detector.detect(text)
        if cscore:
            triggered.add(detector.name)
            score += cscore

    if score > 0:
        signal("detectors-triggered").send(message, user=user, target=target, text=text, triggered=triggered, score=score)

