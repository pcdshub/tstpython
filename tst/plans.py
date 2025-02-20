# Custom plans for use in ued scan gui
from __future__ import annotations

from bluesky.plans import scan
from bluesky.preprocessors import run_decorator, stage_decorator, stub_wrapper
from ophyd.epics_motor import EpicsMotor
from ophyd.pv_positioner import PVPositioner

from .util import get_motor_by_pvname, get_signal_motor_by_pvname


def pv_scan(
    detectors: list,
    pvname: str,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = False,
):
    """
    Scan over a PV
    """
    yield from inner_pv_scan(
        detectors=detectors,
        motor=get_signal_motor_by_pvname(pvname),
        start=start,
        stop=stop,
        num=num,
        subscans=subscans,
        and_back=and_back,
    )


def motor_pv_scan(
    detectors: list,
    pvname: str,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = False,
):
    """
    Scan over a motor record
    """
    yield from inner_pv_scan(
        detectors=detectors,
        motor=get_motor_by_pvname(pvname),
        start=start,
        stop=stop,
        num=num,
        subscans=subscans,
        and_back=and_back,
    )


def inner_pv_scan(
    detectors: list,
    motor: EpicsMotor | PVPositioner,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = False,
):
    @stage_decorator(detectors + [motor])
    @run_decorator(md={})
    def inner(start: int, stop: int):
        for _ in range(subscans):
            yield from stub_wrapper(scan(detectors, motor, start, stop, num))
            if and_back:
                start, stop = stop, start

    yield from inner(start=start, stop=stop)
