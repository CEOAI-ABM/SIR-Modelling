import scipy.integrate as spi
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import pandas as pd

with open("SIR_parameters.json") as f:
    args = json.load(f)
DIR     = "Results\\SIR_{}".format(args["Name"])
os.makedirs(DIR,exist_ok=True)

POP     = args["Population"]
R0      = args["R0"]
DR      = args["Death_Rate"]
GAMMA   = args["GAMMA"] = 1/args["Inc_Period"]
BETA    = args["BETA"]  = GAMMA*R0
TS      = 1       #Time step
Ndays   = args["Days"]       #Number of days
Inf0    = args["Init_Inf"]/args["Population"]
Susp0   = 1-Inf0
Rec0    = 0
Dec0    = 0
INPUT   = (Susp0, Inf0, Rec0,Dec0)
# INPUT   = {'S':Susp0, 'I':Inf0, 'R':Rec0}
strs    = ['S','I','R','D']

def diff_eqs(INP,t):  
    '''The main set of equations'''
    Y   = np.zeros((4))
    V   = dict(zip(strs,INP)) #[Susp,Inf,Rec]   
    Y[0] = - BETA * V['S'] * V['I']
    Y[1] = BETA * V['S'] * V['I'] - GAMMA * V['I']
    Y[2] = GAMMA * V['I'] * (1-DR)
    Y[3] = GAMMA * V['I'] * DR
    return Y   # For odeint

t_start = 0.0; t_end = 1.0*Ndays; t_inc = 1.0*TS
t_range = np.arange(t_start, t_end+t_inc, t_inc)
RES     = spi.odeint(diff_eqs,INPUT,t_range)


plt.subplot(211)
plt.plot(RES[:,0]*POP, '-g', label='Suspectible')
plt.plot(RES[:,1]*POP, '-m', label='Infectious')
plt.plot(RES[:,2]*POP, '-b', label='Recoveries')
plt.plot(RES[:,3]*POP, '-r', label='Deaths')
plt.legend(loc=0)
plt.title('SIR Model for R0='+str(R0)[:4])
# plt.xticks(np.arange(0,Ndays,TS))/
plt.xlabel('Timestep')
plt.ylabel('Number')
plt.grid()

plt.subplot(212)
plt.plot(RES[:,1]*POP, '-r', label='Infectious')
plt.xlabel('Timestep')
plt.ylabel('Infectious')
# plt.show()

df = pd.DataFrame(np.round(RES*POP),columns=["Suspectible",'Infected','Recovered',"Died"])
df.index.name = "Day"

plt.savefig(DIR+"//graph.png")
json.dump(args,open(DIR+"//params.json", 'w'),indent = 4)
df.to_csv(DIR+"//output.csv")