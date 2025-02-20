from pathlib import Path

from hutch_python.load_conf import load

hpy_root = Path(__file__).parent.parent.parent

objs = load(str(hpy_root / "conf.yml"))
# Make all objects available to queueserver
globals().update(**objs)
# Also expand the plan namespace
globals().update(vars(objs["bp"]))
# Also expand the sim namespace to get software-only motors
globals().update(vars(objs["sim"]))


def get_daq_attr(attr: str):
    return getattr(objs["daq"], attr)
