from hutch_python.utils import safe_load
from pcdsdevices.epics_motor import IMS


with safe_load('Example XCS Motor'):
    xcs_user_30 = IMS('XCS:USR:MMS:30', name='xcs_user_30')
