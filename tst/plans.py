# Custom plans for use in ued scan gui
from __future__ import annotations

import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
from psdaq.control.BlueskyScan import BlueskyScan

from .util import get_motor_by_pvname, get_signal_motor_by_pvname


def device_steps(
    detectors: list,
    motor,  # : Moveable, but queueserver type annotation is slightly broken
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Move a motor device from start to stop in n steps as part of a larger run.

    Complete the motion subscans number of times.
    Read data from each detector at each step.
    (Note: the DAQ is a detector)

    This must be used after an open_run bluesky message,
    or within a run_wrapper.

    See the device_scan docstring for more information about input arguments.
    """
    for _ in range(subscans):
        yield from bpp.stub_wrapper(bp.scan(detectors, motor, start, stop, num))
        if and_back:
            start, stop = stop, start


def pv_steps(
    detectors: list,
    pvname: str,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Create a PV motor device from a single PV, and run device_steps.

    PV motors cannot check for completion, but can be used for things like voltages.

    See the device_steps docstring for more information about scan pieces.
    See the device_scan docstring for more information about input arguments.
    """
    yield from device_steps(
        detectors=detectors,
        motor=get_signal_motor_by_pvname(pvname),
        start=start,
        stop=stop,
        num=num,
        subscans=subscans,
        and_back=and_back,
    )


def motor_pv_steps(
    detectors: list,
    pvname: str,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Create an EpicsMotor device from full motor record, and run device_steps.

    EpicsMotor devices have proper move completion information.

    See the device_steps docstring for more information about scan pieces.
    See the device_scan docstring for more information about input arguments.
    """
    yield from device_steps(
        detectors=detectors,
        motor=get_motor_by_pvname(pvname),
        start=start,
        stop=stop,
        num=num,
        subscans=subscans,
        and_back=and_back,
    )


def device_scan(
    detectors: list,
    motor,  # : Moveable, but queueserver type annotation is slightly broken
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Move a motor device from start to stop in num steps, taking data at each point.

    Complete the motion subscans number of times.

    This variant starts and stops both a bluesky and/or a DAQ run before and after
    the steps. To use the DAQ, include it as part of the detectors list.

    If the DAQ is included, the "motors" configuration argument will automatically
    be populated.

    Parameters
    ----------
    detectors: list of readables
        Devices that can be triggered and read in a bluesky scan, such as the DAQ.
    motor: movable
        A device that implements the bluesky movable interface, such as a motor.
    start: number
        A realspace position to start the scan at. This is the first scan point.
    stop: number
        A realspace position to send the scan at. This is the final scan point.
    num: int
        The total number of points in the scan, where the first point is "start",
        the second point is "stop", and the remaining points are interpolated
        linearly.
    subscans: int
        The total number of times to move between start and stop.
    and_back: bool
        If True (default), go back and forth through the subscans.
        If False, go only forward.
    """
    for det in detectors:
        if isinstance(det, BlueskyScan):
            yield from bps.configure(det, motors=[motor])
    yield from bpp.stage_wrapper(
        bpp.run_wrapper(
            device_steps(
                detectors=detectors,
                motor=motor,
                start=start,
                stop=stop,
                num=num,
                subscans=subscans,
                and_back=and_back,
            )
        ),
        detectors + [motor],
    )


def pv_scan(
    detectors: list,
    pvname: str,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Create a PV motor device from a single PV, and run device_scan.

    PV motors cannot check for completion, but can be used for things like voltages.

    See the device_scan docstring for more information about input arguments.
    """
    yield from device_scan(
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
    and_back: bool = True,
):
    """
    Create an EpicsMotor device from full motor record, and run device_steps.

    EpicsMotor devices have proper move completion information.

    See the device_scan docstring for more information about input arguments.
    """
    yield from device_scan(
        detectors=detectors,
        motor=get_motor_by_pvname(pvname),
        start=start,
        stop=stop,
        num=num,
        subscans=subscans,
        and_back=and_back,
    )


def get_daq(daq: BlueskyScan | None = None) -> BlueskyScan:
    """
    Helper to grab the daq object if the user didn't provide it.

    Mostly used as a shim so I can sub in test daq devices.
    """
    if daq is None:
        from hutch.db import daq  # type: ignore # noqa: F401
    return daq


def daq_pv_scan(
    pvname: str,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Variant of pv_scan that always includes the daq as the only detector.

    This is a convenience method only.
    """
    daq = get_daq()
    yield from pv_scan(
        detectors=[daq],
        pvname=pvname,
        start=start,
        stop=stop,
        num=num,
        subscans=subscans,
        and_back=and_back,
    )


def daq_motor_pv_scan(
    pvname: str,
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Variant of pv_scan that always includes the daq as the only detector.

    This is a convenience method only.
    """
    daq = get_daq()
    yield from pv_scan(
        detectors=[daq],
        pvname=pvname,
        start=start,
        stop=stop,
        num=num,
        subscans=subscans,
        and_back=and_back,
    )


def daq_scan_config(
    daq=None,
    motors=None,
    pv_scan_pvs=None,
    motor_pv_scan_pvs=None,
    **kwargs,
):
    """
    Queueserver-compatible DAQ configuration.

    This doesn't do a configure transition, it just sets up parameters.
    You must call this before starting a run for most of the parameters
    to be used.

    Parameters
    ----------
    daq: Daq, optional
        The daq object, which can be passed manually or automatically discovered.
    motors: list of motors, optional
        Motors to tell the daq to include in the data stream.
    pv_scan_pvs: list of str, optional
        PVs to include in the daq data stream.
    motor_pv_scan_pvs: list of str, optional
        Motor PVs to include in the daq data stream.
    kwargs: various
        The other settings to change on the daq. These are left as generic kwargs so
        this function doesn't need to change as the daq libraries update.
    """
    if motors is None:
        motors = []
    else:
        motors = list(motors)
    if pv_scan_pvs is not None:
        motors.extend(get_signal_motor_by_pvname(pv) for pv in pv_scan_pvs)
    if motor_pv_scan_pvs is not None:
        motors.extend(get_motor_by_pvname(pv) for pv in motor_pv_scan_pvs)
    daq = get_daq(daq)
    yield from bps.configure(daq, motors=motors, **kwargs)


def start_run(
    start_daq_run: bool = True,
    daq=None,  # : Optional[BlueskyScan], but queueserver type annotation is hard
    md=None,  # Optional[dict], but queueserver type annotation is broken
):
    """
    Queueserver-compatible run start plan.

    This can be used to begin a bluesky run and a DAQ run.
    This will fail if ran twice in a row with no end_run.

    Scans that themselves open and close runs will fail
    if they are used after this plan. It's meant to be used
    in conjunction with the *_steps plan to assemble
    arbitrary custom trajectories.

    Note that the run doesn't officially start until we
    take the first event of data.
    """
    yield from bps.open_run(md=md)
    if start_daq_run:
        daq = get_daq(daq)
        yield from bps.stage(daq)


def end_run(
    end_daq_run: bool = True,
    daq=None,  # : BlueskyScan | None, but queueserver type annotation is hard
):
    """
    Queueserver-compatible run end plan.

    This can be used to end a bluesky run and a DAQ run.
    This will fail if ran twice in a row, or if called
    without first running start_run.
    """
    yield from bps.close_run()
    if end_daq_run:
        daq = get_daq(daq)
        yield from bps.unstage(daq)
