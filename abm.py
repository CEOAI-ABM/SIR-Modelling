import scipy.integrate as spi
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import src

with open("ABM_parameters.json") as f:
    args = json.load(f)
DIR     = "Results\\"+args["Name"]
os.makedirs(DIR,exist_ok=True)

src.simulate(args)