from hutch_python.utils import safe_load

with safe_load("disable scan pvs"):
    from tst.db import scan_pvs  # type: ignore

    scan_pvs.disable()


with safe_load("coupled sim motor and det"):
    from ophyd.sim import det as sim_det

    sim_det.kind = "hinted"
    from ophyd.sim import SynAxis

    SynAxis.move = SynAxis.set


with safe_load("test plans from ued"):
    from .plans import pv_scan, motor_pv_scan  # noqa: F401, I001
