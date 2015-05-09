
detectors = {}


def detector(detector_name):
    def detector_dec(f):
        if detector_name in detectors:
            print("ERROR: Detector \"{}\" is a duplicate. Skipping.".format(detector_name))
            return f

        detectors[detector_name] = f
        return f
    return detector_dec
