import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

Nos = 9
R0 = np.linspace(1,4,Nos)
for i in R0:
    NAME = str(i)

    ABM_DIR = "Results\\ABM_{}".format(NAME)
    SIR_DIR = "Results\\SIR_{}".format(NAME)

    abm_df = pd.read_csv(ABM_DIR+"\\sir_df.csv")
    sir_df = pd.read_csv(SIR_DIR+"\\output.csv")
    cit_df = pd.read_csv(ABM_DIR+'\\register.csv')

    print(abm_df.columns)
    cols = ['Suspectible','Infected','Recovered']
    fig = plt.figure(figsize=(10,5*len(cols)))
    for i,colname in enumerate(cols):
        ax  = plt.subplot(len(cols),1,i+1)
        plt.plot(abm_df['Day'],abm_df[colname])
        plt.plot(sir_df['Day'],sir_df[colname])
        plt.legend(['ABM','SIR'])
        plt.xlabel('Days')
        plt.ylabel(colname)
        # plt.title("Days vs "+colname)
        plt.grid()
    cols = ['Infected','Recovered','Died']
    fig = plt.figure(figsize=(10,5*len(cols)))
    for i,colname in enumerate(cols):
        ax  = plt.subplot(len(cols),1,i+1)
        count = cit_df[colname].value_counts()
        A = sorted(count.index)[1:]
        plt.plot(A,count[A],label='ABM_{}'.format(colname))
        plt.plot(sir_df['Day'],sir_df[colname],label='SIR_{}'.format(colname))
        plt.xlabel('Days')
        plt.ylabel(colname)
    plt.legend()
    plt.grid()
    plt.show()