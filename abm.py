import numpy as np
import json
import os
import src
import multiprocessing as mp

def do(args,R0):
    DIR     = "Results\\ABM_{}".format(R0)
    args["R0"] = R0
    os.makedirs(DIR,exist_ok=True)

    src.simulate(args,DIR,SAVE=False,LOAD=False)

def do_normal(args):
    DIR     = "Results\\ABM_{}".format(args["Name"])
    os.makedirs(DIR,exist_ok=True)

    src.simulate(args,DIR,SAVE=True,LOAD=False)

if __name__ == '__main__':
    with open("ABM_parameters.json") as f:
        args = json.load(f)

    if args["Name"] == "MULTI":
        Nos = 9
        R0 = np.linspace(1,4,Nos)
        pool = mp.Pool(processes=8)
        for i in range(Nos):
            pool.apply_async(do, args = (args,R0[i]))
        pool.close()
        pool.join()
    else:
        do_normal(args)