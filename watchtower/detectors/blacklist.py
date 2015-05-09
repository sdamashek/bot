from watchtower.models import BlacklistEntry
from watchtower.detector import detector
import re


@detector("blacklisting")
def detect(message):
    cscore = 0
    patterns = list(map(lambda k: (k.pattern, k.weight), BlacklistEntry().select()))
    for pattern, weight in patterns:
        if re.match(pattern, message) is not None:
            cscore += weight
    return cscore
