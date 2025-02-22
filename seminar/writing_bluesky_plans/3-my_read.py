from functools import partial

import bluesky.plan_stubs as bps
import bluesky.plans as bp


def increment_counter():
    print("Increment the counter!")


def my_read(detectors):
    increment_counter()
    yield from bps.trigger_and_read(detectors)


my_scan = partial(bp.scan, per_step=partial(bps.one_nd_step, take_reading=my_read))
