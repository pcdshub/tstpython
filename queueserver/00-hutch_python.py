import os.path

from hutch_python.load_conf import load
from hutch_python.log_setup import setup_logging
from pcdsdaq.sim import set_sim_mode

# Do the normal hutch-python loading
set_sim_mode(True)
cfg = '/cds/group/pcds/pyps/apps/hutch-python/tst/conf.yml'
setup_logging(dir_logs=os.path.join(os.path.dirname(cfg), 'logs'))
objs = load(cfg=cfg)

# Make some post-adjustments for queue-server
# Disable the bec plots for the server process (keep the table)
objs['bec'].disable_plots()
# Make all objects available to queue-server
globals().update(objs)
# Additionally expand the plan namespace so that the queue-server sees it
globals().update(vars(objs['bp']))
# Additionally expand the experiment object so that the queue-server sees it
try:
    globals().update(vars(objs['user']))
except KeyError:
    pass
