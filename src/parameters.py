import os
import sys
import pickle
import pandas as pd
import numpy as np
import multiprocessing as mp
import ctypes 
import warnings
from .utils import get_Numbers

warnings.filterwarnings("ignore", category=FutureWarning) 
from typing import NamedTuple


class Parameters:
	def __init__(self):
		"""__init__ 
		Converts a Shapefile into relvant Regions 

		Args:
			FILENAME (str): [description]
			indexcol (str): [description]
		"""
		self.use_shapefiles = None
	def initialize_params(self,Files_Zip=None, indexcol=None, load_pickle=False, save_pickle=False,**kwargs): 
		#============================================================================================
		#---------------------- City Population Parameters ------------------------------------------
		#============================================================================================
		self.Population 		= kwargs.get("Population", 100000)
		self.Family_size 		= kwargs.get("Family_Size",[5,1])
		self.Density 			= kwargs.get("Density",328)
		self.Cityname			= kwargs.get("City","Generic") #Name of the city
		self.Population_groups 	=  kwargs.get("Pop_Groups", [5,18,25,60,80,150]) #Max ages of different groups
		self.Population_Dist	=  kwargs.get("Pop_Dist", [0.131,0.242,0.126,0.346,0.075,0.080]) # Population distribution between each groups
		self.perlakh			= self.Population/100000
		#============================================================================================
		#-------------------------- Workplace  Parameters -------------------------------------------
		#============================================================================================
		self.sectors 			= kwargs.get("Sectors", ['Generic'])
		self.Workplace_Params 	=  {
								"General":  {"N":[1.0],"E":[self.Population],"V":[8,2]}
		}
		self.Workplace_Params 	= kwargs.get("SecVirus",self.Workplace_Params)
		#============================================================================================
		#--------------------------- Transport Parameters ------------------------------------------
		#============================================================================================
		#Format:  Region[id]: [list of expected people at diff size of trans,list of expected people in those trans 
		#Transporation Model PerDay Model
		
		self.ExpStops 			= kwargs.get("ExpStops", 4)
		self.VarStops 			= kwargs.get("VarStops", 1)
		
		self.NumRoutes			= kwargs.get("NumRoutes", int(30*self.perlakh))
		self.Prob_use_TN		= kwargs.get("UseTran", 0.17)
		BusCap 					= kwargs.get("BusCap", 30)
		self.NumBuses 			= (self.Prob_use_TN*self.Population)//BusCap
		self.LocalTransport_zip = [self.ExpStops, self.VarStops, self.NumBuses]
		#============================================================================================
		#--------------------------- Inter-city Transport Parameters --------------------------------
		#============================================================================================
		# This will be multiplied by the (population of the region)/(total population of city)
		#self.ExpICT            	 	= kwargs.get("ExpICT", 12500) # Chosen from Kolkata statistics - http://www.knowindia.net/aviation3.html
		#self.VarICT             	= kwargs.get("VarICT", 2000)
		self.ProbLocalTravel    	= kwargs.get("ProbLocalTravel", 0.7) # Probability of a traveller being a local  
		
		#self.IFP 		        	= kwargs.get("IFP", 0.001) 

		self.ICT_Population_groups 	= kwargs.get("ICT_Population_groups" ,[5,18,25,60,80,150]) #Max ages of different groups
		self.ICT_Population_Dist	= kwargs.get("ICT_Population_Dist" ,[0.131,0.242,0.126,0.346,0.075,0.080]) # Population distribution between each groups
		#============================================================================================
		#-------------------------- Employment Params----- ------------------------------------------
		#============================================================================================
		if "Empl_Dist" in kwargs:
			self.Employment_params = dict(zip(self.Population_groups,kwargs["Empl_Dist"]))
		else:
			self.Employment_params = {
				5 	: [0.00, 0.0000, 0.0000, 0.00000, 0.000, 0.000000, 0.000, 0.000, 0.00, 0.0000, 0.00000, 1.0],
				18 	: [0.60, 0.0005, 0.0005, 0.00018, 0.005, 0.000000, 0.000, 0.100, 0.25, 0.0001, 0.04372, 0.0],
				25 	: [0.10, 0.0170, 0.0120, 0.00100, 0.050, 0.000000, 0.011, 0.120, 0.35, 0.2000, 0.13900, 0.0],
				60 	: [0.01, 0.0190, 0.0100, 0.00050, 0.065, 0.000012, 0.010, 0.170, 0.30, 0.3000, 0.11548, 0.0],
				80 	: [0.00, 0.0140, 0.0000, 0.00050, 0.001, 0.000020, 0.001, 0.001, 0.06, 0.1200, 0.10248, 0.7],
				150 : [0.00, 0.0000, 0.0000, 0.00000, 0.000, 0.000000, 0.000, 0.000, 0.00, 0.0000, 0.00000, 1.0]
			}
		
		
		#============================================================================================
		#-------------------------- Transaction  Parameters ------------------------------------------
		#============================================================================================
		self.Transaction_ProbablityOfPurchase 	= kwargs.get("ProbPurchase", 0.5)
		self.Transaction_MinGroceryRequirement	= 19
		self.Transaction_zip =[self.Transaction_ProbablityOfPurchase, self.Transaction_MinGroceryRequirement]
		#============================================================================================
		#-------------------------- Virus  Parameters ------------------------------------------
		#============================================================================================
		self.Virus_Name 			= "CoronaVirus"
		self.Virus_R0 				= kwargs.get("R0", 2.0)		


		if "Virus_Params" in kwargs:
			self.Virus_Params = kwargs["Virus_Params"]
		else:
			self.Virus_Params = {
			'Transport' : {'Time':2.2283,'Distance':1}, #See spatial_init.py for calc of this
			'Home' 		: {'Time':16,'Distance':1},
			'Grocery'	: {'Time':0.5,'Distance':4},
			'Unemployed': {'Time':8,'Distance':1},
			'Random'	: {'Time':1,'Distance':2}, #This is Random transmissions within the region boundary
			}

		
		self.Virus_DistanceDist 		= {"Constant":0.128,"Ratio":2.02}
		self.Virus_Deathrates 			= kwargs.get("Death_Rates", [0.01/2,0.005/2,0.01/2,0.01/2,0.04/2,0.30/2]) #Between age groups in agedist model
		self.Virus_IncubationPeriod		= kwargs.get("Inc_Period", [6,6,8,5,2,2]) 	#Between Age groups 
		self.Virus_ExpectedCureDays		= kwargs.get("Cure_Days", 14) 			#Days to cure
		self.Virus_PerDayDeathRate		= [EE/self.Virus_ExpectedCureDays for EE in self.Virus_Deathrates]
		self.Virus_ProbSeverity 		= kwargs.get("Virus_ProbSeverity", [[0.70,0.26,0.04],
																			[0.80,0.16,0.04],
																			[0.80,0.16,0.04], 
																			[0.95,0.04,0.01],
																			[0.60,0.30,0.10],
																			[0.40,0.40,0.20],
																			[0.10,0.40,0.50]])  # Mild, Medicore, Severe between Age Groups

		self.Virus_Prob_ContactTracing = kwargs.get("Virus_Prob_ContactTracing", 0.9)

		#Do not change this list during a sim. Can be edited here in parameters only. #Removing a mode will 
		#permanently stop transmission via that mode for all regions (different from sector lock)
		self.transmissionModes = ['Home', 'Transport', 'Grocery', 'Unemployed','Random'] + self.sectors 

		self.PseudoSymptoms_Prob = kwargs.get("PPseudoSymptoms", 0.00) # Probability Keeping it random for now, later adjust such that should be such that the positive rate is nearly 5-10%

		#self.Virus_zip =[self.Virus_Name, self.Virus_Params,self.Virus_PerDayDeathRate, self.Virus_IncubationPeriod, self.Virus_ExpectedCureDays, self.Virus_InitialTestingCap,
		#			self.Virus_FullCapRatio, self.Virus_Prob_ContactTracing,self.Virus_ProbSeverity]
		#============================================================================================
		#-------------------------- Pre Conditions Params----- ------------------------------------------
		#============================================================================================
		self.Comorbidty_matrix = {
		'ComorbidX' 	: [0.00,0.00,0.00,0.00,0.00,0.00] #Percentage of Population getting deasese X
		}

		self.Comorbidty_matrix = kwargs.get("Comorbidity_matrix", self.Comorbidty_matrix)

		self.Comorbidty_weights = {
		'ComorbidX' 	: [0.1,0.7,0.2] 			# Probablity of increase in Severtiy if you have Disease X
		}

		self.Workplace_Params = get_Numbers(self)

		self.SimStartDay 		= kwargs.get("SimStartDay", "2020-05-03") # Day when sim starts 
		self.SIMULATION_DAYS 	= kwargs.get("Days",300)
		self.INIT_INFECTED		= kwargs.get("Init_Inf", 10) #Number of People Initially infected 
		self.PROCESSES 			= kwargs.get("Processes", 16)
		self.ComplianceRate  	= kwargs.get("StartCR", 0.8)
		
		# self.HOLD 			= mp.Value(ctypes.c_bool, 0) #Hold the simulation
		self.SAVE_TO_FILE 		= True 
		self.SHOW_MAP 			= True 
		self.DISPLAY_AS_REGION 	= True #If false will display as per house, which can be extremely slow
		#============================================================================================
		#-------------------------- Lockdown Params----- ---------------------------------
		#============================================================================================
		self.LockdownPhases 	= kwargs.get("LockdownPhases", [])  
		self.CR_Phases 			= kwargs.get("CR_Phases", []) 
		self.IFP_Phases 		= kwargs.get("IFP_Phases", []) 
		#============================================================================================
		#-------------------------- Testing and Tracing Params----- ---------------------------------
		#============================================================================================
		self.TestingOn 				= kwargs.get("TestingOn", True) # True if testing is on, else False
		self.TracingOn 				= kwargs.get("TracingOn", True) # True if tracing is on, else False
		self.InitPTR  				= kwargs.get("PTR", 0.05)		

		try:
			df_testing 				= pd.read_pickle('Database/Testing/testing_cap.pkl')
			self.Virus_TestingCap 	= df_testing[self.SimStartDay:]['Total Tested in Kolkata Today'].to_list()	
		except:
			print('\033[93m' ,"WARNING: Testing Time series is not present, taking default value",'\033[0m',sep="")
			self.Virus_TestingCap 	= [kwargs.get("TestingCap", 1000) for _ in range(self.SIMULATION_DAYS + 5)]
		
		try:
			df_ict 					= pd.read_pickle('Database/Kolkata/Kolkata_ICT.pkl')
			self.ExpICT_list 		= df_ict[self.SimStartDay:]['ExpICT'].to_list()  
		except:
			print('\033[93m' ,"WARNING: Inter City Travellors Time series is not present, taking default value",'\033[0m',sep="")
			self.ExpICT_list	 	= [kwargs.get("ExpICT", 3000) for _ in range(self.SIMULATION_DAYS + 5)]

		"""
		try:
			self.DailyIFP	 		= pd.read_pickle('Database/Kolkata/Kolkata_IFP_Europe_Like.pkl')	
			self.DailyIFP			= self.DailyIFP['IFP'][self.SimStartDay:].to_list()	
		except:
			print('\033[93m' ,"WARNING: Daily Infected Probablity Time series is not present, taking default value",'\033[0m',sep="")
			self.DailyIFP 			= [kwargs.get('IFP', 0.01) for i in range(self.SIMULATION_DAYS.value + 5)]
		"""

		self.IFP                	= kwargs.get("StartIFP", 0.001)	
		self.CommON 				= kwargs.get("Commerce_On", True)	
		self.Sim_Name 				= kwargs.get("Name", 'Test')	
	
