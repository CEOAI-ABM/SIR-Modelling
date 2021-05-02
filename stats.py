import numpy as np
import pandas as pd
def stat(NAME):
    ABM_DIR = "Results\\ABM_{}".format(NAME)
    SIR_DIR = "Results\\SIR_{}".format(NAME)
   
    abm_df = pd.read_csv(ABM_DIR+"\\sir_df.csv")
    sir_df = pd.read_csv(SIR_DIR+"\\output.csv")
    cit_df = pd.read_csv(ABM_DIR+'\\register.csv')

    print("R0=",NAME)
    PID = sir_df.iloc[sir_df['Infected'].argmax()]['Day']
    print("Peak infection day=",PID,'\n')
    print("Highest Case Load=",sir_df.max()['Infected'],'\n') 
    print("Last Day Cases=",10000-sir_df.iloc[-1]['Suspectible'],'\n')
    print("-----------------------------------------------")
    PID1= abm_df.iloc[abm_df['Infected'].argmax()]['Day']
    print("Peak infection day=",PID1,'\n')
    print("Highest Case Load=",abm_df.max()['Infected'],'\n')
    print("Last Day Cases=",10000-abm_df.iloc[-1]['Suspectible'],'\n')
    
    E1 = 10000-abm_df['Suspectible']
    E2 = 10000-sir_df['Suspectible'] 
    diff = abs(E1-E2.shift(int(PID1-PID)))/E2.shift(int(PID1-PID))
    diff.dropna(inplace=True)
    Accuracy = (diff<0.1).value_counts()
    print(Accuracy)
    try: 
        print("Accuracy",NAME,":",Accuracy.loc[True]/(Accuracy.loc[True]+Accuracy.loc[False]))
    except KeyError:
        print("Accuracy",NAME,":",0)
    print("===============================================")
def only_abm(NAME):
    ABM_DIR = "Results\\ABM_{}".format(NAME)
   
    abm_df = pd.read_csv(ABM_DIR+"\\sir_df.csv")
    cit_df = pd.read_csv(ABM_DIR+'\\register.csv')

    print("R0=",NAME)
    PID1= abm_df.iloc[abm_df['Infected'].argmax()]['Day']
    print("Peak infection day=",PID1,'\n')
    print("Highest Case Load=",abm_df.max()['Infected'],'\n')
    print("Last Day Cases=",10000-abm_df.iloc[-1]['Suspectible'],'\n')
    
# SAVE_DIR = "Plots\\Paper"
# os.makedirs(SAVE_DIR,exist_ok=True)
# Nos = 9
# R0 = np.linspace(1,4,Nos)
# for i in R0:
#     NAME = str(i)
#     stat(NAME)
only_abm("Social_Distancing")