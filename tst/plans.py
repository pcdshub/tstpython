# Custom plans for use in ued scan gui
from __future__ import annotations

import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
from psdaq.control.BlueskyScan import BlueskyScan

from .util import get_motor_by_pvname, get_signal_motor_by_pvname


def device_steps(
    detectors,  # : list[Readable], but broken annotations
    motor,  # : Moveable, but queueserver type annotation is slightly broken
    start: float,
    stop: float,
    num: int,
    subscans: int = 1,
    and_back: bool = True,
):
    """
    Move a motor device from start to stop in n steps as part of a larger DAQ run.

    Complete the motion subscans number of times.
    Read data from each detector at each step.
    (Note: the DAQ is a detector)

    This is its own Bluesky run for queueserver compatibility, but it will not
    end the DAQ run, unlike device_scan.

    See the device_scan docstring for more information about input arguments.
    """

    @bpp.run_decorator(md=None)
    def _inner(start: float, stop: float):
        for _ in range(subscans):
            yield from bpp.stub_wrapper(bp.scan(detectors, motor, start, stop, num))
            if and_back:
                start, stop = stop, start

    yield from _inner(start, stop)


def pv_steps(
    detectors,  # : list[Readable], but broken annotations
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
    detectors,  # : list[Readable], but broken annotations
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
    detectors,  # : list[Readable], but broken annotations
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

    See daq_device_scan for a variant that automatically includes the daq argument
    as the sole detector.

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
    yield from bpp.stage_wrapper(
        device_steps(
            detectors=detectors,
            motor=motor,
            start=start,
            stop=stop,
            num=num,
            subscans=subscans,
            and_back=and_back,
        ),
        detectors + [motor],
    )


def pv_scan(
    detectors,  # : list[Readable], but broken annotations
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
    See daq_pv_scan for a variant that automatically includes the DAQ.
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
    detectors,  # : list[Readable], but broken annotations
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
    See daq_motor_pv_scan for a variant that automatically includes the daq.
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
        from tst.db import daq  # type: ignore # noqa: F401
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


def daq_start_run(
    daq=None,  # : Optional[BlueskyScan], but queueserver type annotation is hard
):
    """
    Queueserver-compatible DAQ run start plan.

    This can be used to begin a DAQ run.
    Internally, it sets the DAQ to the "connected" state, so that
    at the first data point we "configure" and "enable" the DAQ,
    at which point the run officially starts.

    Note that you should not call this twice in a row, due to the
    implementation details this will actually end the run.

    Scans that themselves start and stop the runs will lead to
    confusing behavior when combined with this plan.
    This is meant to be used in conjunction with the *_steps plans
    to assemble arbitrary custom trajectories.

    Note that the run doesn't officially start until we
    take the first event of data.

    Internally, this runs daq.stage, which is a generic function
    to prepare DAQ for a run. The precise details of this function
    are subject to change.
    """
    daq = get_daq(daq)
    yield from bps.stage(daq)


def daq_stop_run(
    daq=None,  # : BlueskyScan | None, but queueserver type annotation is hard
):
    """
    Queueserver-compatible DAQ run end plan.

    This can be used to end a DAQ run.

    Internally, this runs daq.unstage, which is a generic function
    to bring a DAQ out of a run. The precise details of this function
    are subject to change.
    """
    daq = get_daq(daq)
    yield from bps.unstage(daq)
