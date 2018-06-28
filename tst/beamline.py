from hutch_python.utils import safe_load


with safe_load('example xcs motor'):
    from pcdsdevices.epics_motor import IMS
    xcs_user_30 = IMS('XCS:USR:MMS:30', name='xcs_user_30')


with safe_load('coupled sim motor and det'):
    from ophyd.sim import motor as sim_motor, det as sim_det
    sim_det.kind = 'hinted'
