from functools import partial
 
def my_step(detectors, step, pos_cache, take_reading=bps.trigger_and_read):
    motors = step.keys()
    yield from before_move()
    yield from bps.move_per_step(step, pos_cache)
    yield from after_move()
    yield from take_reading(list(detectors) + list(motors))
 
my_scan = partial(bp.scan, per_step=my_step)
