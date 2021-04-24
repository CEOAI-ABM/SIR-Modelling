from .calibration import calibrate
from .parameters import Parameters
from .city import city
from .utils import timecalc
import pickle 
import os
def simulate(args,SAVE=False,LOAD=False):
    Tym = timecalc()

    Tym.add_checkpoint(0)
    
    pm = Parameters()
    pm.initialize_params(**args)

    Tym.add_checkpoint(1)
    
    C = calibrate(pm)
    
    Tym.add_checkpoint(2)

    if LOAD:
        try:
            print("Loading Data from Pickle")
            DIR     = "Data\\"+pm.Sim_Name 
            with open(DIR+'\\City.pickle', 'rb') as f:
                City = pickle.load(f)
        except:
            print("ERROR: Fail to Load, creating New One")
            City = city(pm)
            City.initialize()

    else:
        City = city(pm)
        City.initialize()

    Tym.add_checkpoint(3)

    City.updateratetransmissions(pm,c=C)

    City.Citizens[0].infected()
    for i in range(100):
        City.daily_transmissions()
        print(len(City.AFreeP ))


    Tym.add_checkpoint(4)
    Tym.print_result()
    if SAVE and not LOAD:
        DIR     = "Data\\"+pm.Sim_Name 
        os.makedirs(DIR,exist_ok=True)
        with open(DIR+'\\City.pickle', 'wb') as f:
            pickle.dump(City, f, pickle.HIGHEST_PROTOCOL)
    
    # Declare R0
    # Declare Workplaces
    # Declare 