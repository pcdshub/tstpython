from pathlib import Path

from hutch_python.load_conf import load

hpy_root = Path(__file__).parent.parent.parent

objs = load(str(hpy_root / "conf.yml"))
globals().update(**objs)
