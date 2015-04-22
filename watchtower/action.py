from blinker import signal

triggered = signal("detectors-triggered")
@triggered.connect
def handle_triggered(message, user, target, text, score):
    if 0.75 > score > 0.25:
        message.client.writeln("KICK {} {} :spam detector triggered".format(target, user.nick))
