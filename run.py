import watchtower.irc

import logging
logging.basicConfig(level=logging.INFO)

import signal
def shell(dank, memes):
    import code
    code.interact(local=locals())
signal.signal(signal.SIGUSR1, shell)

import asyncio
asyncio.get_event_loop().run_forever()
