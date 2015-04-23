import logging
import threading
logging.basicConfig(level=logging.INFO)

shell_banner = """This is the debug shell for Watchtower.
Be careful, as this shell runs in the same environment as the bot, only in a
separate thread. Watchtower is generally not thread-safe, so please be careful
in this environment.

`watchtower.irc.registry` is the channel tracking registry.
`watchtower.irc.bot` is the IRCProtocol object.
`watchtower.irc.asyncirc` is our asyncirc import.
"""

import code
def shell():
    namespace = locals()
    namespace.update(globals())
    code.interact(banner=shell_banner, local=namespace)

def launch_shell(_, _2):
    threading.Thread(target=shell).start()

import signal
signal.signal(signal.SIGUSR1, launch_shell)

import watchtower.detection
import watchtower.action

import watchtower.irc
import asyncio
asyncio.get_event_loop().run_forever()
