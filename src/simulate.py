from .calibration import calibrate
from .parameters import Parameters
from .city import city
from .utils import timecalc
import pickle 
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from matplotlib.lines import Line2D
def plot(data:dict,region,pm,plotwhat,SAVE_TO_FILE,SAVEDIR):
    """Plots Data for the data

        Args:
        data (dict): data of day, Asymtomatic, Hospitalized, died, recovered, printdata, repronumber, Cumulative,Positive and Negative tested
        kharagpur (city object): object of city
        plotwhat (dict): bools whether to plot Lockdown, CapLine, Asymtomatic, Hospitalized, died, recovered, Cumulative, PositiveTested
        SAVE_TO_FILE (bool): whether to saveself.ComplianceRate = self.CR_before_CZto file
        SAVEDIR (str): string where to save		
    """
    legend_data = []
    # Plotting
    
    if plotwhat['CapLine']:
        x,y = [0,data['day'][-1]],[region.SectorHolder['Healthcare'].PeopleInSector(),region.SectorHolder['Healthcare'].PeopleInSector()]
        
        # x,y = [0,data['day'][-1]],[kharagpur.Workplace_model['Healthcare'].PeopleInCommercials,kharagpur.Workplace_model['Healthcare'].PeopleInCommercials]
        line = Line2D(x,y,color='Red',linestyle='--')
        plt.gca().add_line(line)
        legend_data.append('Hospital Cap')
    plt.title("ABM Plot at R0="+str(pm.Virus_R0))

    maximum 	= 0
    
    for var in data.keys():
        if var in plotwhat.keys() and plotwhat[var]:
            plt.plot(data['day'],data[var])
            maximum = max(data[var][-1],maximum)
            legend_data.append(var)

    if plotwhat['Lockdown']:
        for elt in region.LockdownLog:
            rect = plt.Rectangle((elt[0],0),elt[1]-elt[0],data['Cumulative'][-1],linewidth=1,edgecolor='r',facecolor=mcolors.CSS4_COLORS['lightgrey'])
            plt.gca().add_patch(rect)
    try:
        #plt.gca().yaxis.set_ticks(np.arange(0, maximum, int((maximum-0)/20)))
        #plt.gca().xaxis.set_ticks(np.arange(0, data['day'][-1], 10))
        plt.xlabel('Data')
        plt.ylabel('No_of_people')
        plt.legend(legend_data)
        plt.grid()
        
        if SAVE_TO_FILE:
            plt.savefig(SAVEDIR+"plot.png")
        return plt
    except:
        pass

def load_city(LOAD,pm):
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
    return City

def run(City,pm,C,SAVEDIR):
    SAVEDIR +='\\'
    SIMULATION_END_DATE 	= pm.SIMULATION_DAYS
    feed_dict 			= np.zeros((SIMULATION_END_DATE+1,9))
    printdata 			= [[] for i in range(SIMULATION_END_DATE+1)]
    SAVE_TO_FILE        = True
    df_transmissions 	= pd.DataFrame()
    printdata[0]        = [0,0,0,0,0,0,0,0,0,0,0,0] 
    City.updateratetransmissions(pm,c=C,r=pm.SD_Ratio)
    # print(City.TR)
    # print(list(map(lambda x:City.TR[x]*pm.Population,City.TR.keys())))

    City.Citizens[0].infected(City.Today)
    lockdown_Start = 1000000
    lockdown_End   = 1000000
    X              = 1000
    # updateratetransmissions

    for i in range(pm.SIMULATION_DAYS):
        City.daily_lockdown()
        # if City.Today >= lockdown_Start:
        #     City.impose_lockdown(lockdown_Start,lockdown_End)
        #     lockdown_Start = 1000000
        # if City.Today > lockdown_End:
        #     City.lift_lockdown()
        #     lockdown_End = 1000000
        
        City.daily_transactions()
        City.daily_transmissions()
        
        # print(len(City.AFreeP ))
        print("Day:",City.Today, "R0:",pm.Virus_R0)
        # print(City.print_status())
        City.Today+=1
        
        TAF = len(City.AFreeP)
        TAQ = len(City.AQuarentinedP)
        TSI = len(City.SIsolatedP)
        TSH = len(City.SHospitalizedP)
        TSC = len(City.SIcuP)
        TRR = len(City.RRecoveredP)
        TRD = len(City.RDiedP)
        RR  = City.get_reproduction_rate()
        PT  = len(City.TestedP['Positive'])
        NT  = len(City.TestedP['Negative'])
        TCC = TAF+TAQ+TSI+TSH+TSC+TRR+TRD

        feed_dict[City.Today,0] = City.Today 	#day
        feed_dict[City.Today,1] = TAF+TAQ 		#infected
        feed_dict[City.Today,2] = TSI+TSH+TSC    	#hospitalized
        feed_dict[City.Today,3] = TRD         	#died
        feed_dict[City.Today,4] = TRR         	#Recovered
        feed_dict[City.Today,5] = RR          	#repornumber
        feed_dict[City.Today,6] = PT 				#Positively Tested    
        feed_dict[City.Today,7] = NT 				#Negative Tested  
        feed_dict[City.Today,8] = TCC 			#Total Cumulative cases
        printdata[City.Today] = [City.Today,TCC,TAF,TAQ,TSI,TSH,TSC,TRR,TRD,RR,PT,NT] 
        City.clear_transactions()
        # if PT>X:
        #     lockdown_Start= City.Today-1
        #     lockdown_End= City.Today+40
        #     X=10000
    if City.Today != 0:    
        data = {}
        sir = {}
        data_cols = ["Day","Cumulative True Cases","Free","Quarentined","Isolated","Hospitalized","ICU", "Recoveries","Deaths","Rough Repo Number","Positively Tested","Negatively Tested"]		
        
        data['day']				= feed_dict[:,0]
        data['Asymtomatic']		= feed_dict[:,1]
        data['Hospitalized']	= feed_dict[:,2]
        data['died']			= feed_dict[:,3]
        data['recovered']		= feed_dict[:,4]
        data['printdata']		= printdata
        data['repronumber']		= feed_dict[:,5]
        data['positive_tested']	= feed_dict[:,6]
        data['negative_tested']	= feed_dict[:,7]
        data['Cumulative']		= feed_dict[:,8]

        temp = np.array(printdata)
        sir['Day'] = temp[:,0]
        sir['Suspectible'] = pm.Population - temp[:,1]
        sir['Infected']    = temp[:,2]
        sir['Recovered']   = np.sum(temp[:,3:8],axis=1)
        sir['Died']        = temp[:,8]
        if SAVE_TO_FILE:
            # f = open(SAVEDIR+"log.txt", "w")
            # #f.write(tabulate(pm.table))
            # f.write(tabulate(region.print_region_data(sectors, get=True)))
            # f.write('\n')
            # f.write(tabulate(data['printdata'], headers=data_cols))
            # f.close()
            
            df_register = City.citizen_register()

            df_register.to_csv(SAVEDIR+'register.csv', index=False)   

            # Save results_df
            results_df = pd.DataFrame(data['printdata'], columns = data_cols)
            sir_df  = pd.DataFrame(sir)
            # results_df.loc[len(results_df)-1, 'FINAL_Positive_Tested_Death'] = len(df_register[np.logical_and(df_register['State'] == 'Died', df_register['Testing_State'] == 'Tested_Positive')])
            
            results_df.to_csv(SAVEDIR+'results_df.csv', index=False)
            sir_df.to_csv(SAVEDIR+'sir_df.csv', index=False)
        plotwhat = {'Lockdown':True, 'CapLine':True, 'Asymtomatic':False,
                    'Hospitalized':True, 'died':True, 'recovered':True, 'Cumulative':True,'positive_tested':True}
        if len(City.LockdownLog) == 0:
            plotwhat['Lockdown'] = False
        plot(data,City,pm,plotwhat,SAVE_TO_FILE,SAVEDIR)

def simulate(args,DIR,SAVE=False,LOAD=False):
    Tym = timecalc()

    Tym.add_checkpoint(0)
    
    pm = Parameters()
    pm.initialize_params(**args)

    Tym.add_checkpoint(1)
    
    C = calibrate(pm)

    Tym.add_checkpoint(2)

    City = load_city(LOAD,pm)
    if SAVE and not LOAD:
        DIRD     = "Data\\"+pm.Sim_Name 
        os.makedirs(DIRD,exist_ok=True)
        with open(DIRD+'\\City.pickle', 'wb') as f:
            pickle.dump(City, f, pickle.HIGHEST_PROTOCOL)

    Tym.add_checkpoint(3)

    run(City,pm,C,DIR)


    Tym.add_checkpoint(4)

    Tym.print_result()

    
    
    # Declare R0
    # Declare Workplaces
    # Declare 