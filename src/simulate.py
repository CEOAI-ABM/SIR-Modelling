from .calibration import calibrate
from .parameters import Parameters
def simulate(args):
    pm = Parameters()
    pm.initialize_params(**args)
    calibrate(pm)

    # Declare R0
    # Declare Workplaces
    # Declare 