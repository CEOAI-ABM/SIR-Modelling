import pandas as pd
import matplotlib.pyplot as plt
NAME = "R03"

ABM_DIR = "Results\\ABM_{}".format(NAME)
SIR_DIR = "Results\\SIR_{}".format(NAME)

abm_df = pd.read_csv(ABM_DIR+"\\sir_df.csv")
sir_df = pd.read_csv(SIR_DIR+"\\output.csv")
cit_df = pd.read_csv(ABM_DIR+'\\register.csv')

print(abm_df.columns)
cols = ['Suspectible','Infected','Recovered']
fig = plt.figure(figsize=(10,30*len(cols)))
for i,colname in enumerate(cols):
    ax  = plt.subplot(len(cols),1,i+1)
    plt.plot(abm_df['Day'],abm_df[colname])
    plt.plot(sir_df['Day'],sir_df[colname])
    plt.legend(['ABM','SIR'])
    plt.xlabel('Days')
    plt.ylabel(colname)
    # plt.title("Days vs "+colname)
    plt.grid()
fig = plt.figure(figsize=(10,30))
ax  = plt.subplot(3,1,1)
cit_df['Infected'].plot.hist(bins=101, alpha=1)
plt.xlabel('Days')
plt.ylabel('Infected')
ax  = plt.subplot(3,1,2)
cit_df['Recovered'].plot.hist(bins=101, alpha=1)
plt.xlabel('Days')
plt.ylabel('Recovered')
# plt.plot(abm_df['Day'],abm_df['Infected'])
# plt.plot(sir_df['Day'],sir_df['Infected'])
# plt.legend(['ABM','SIR'])
# plt.xlabel('Days')
# plt.ylabel('No of People')
plt.show()