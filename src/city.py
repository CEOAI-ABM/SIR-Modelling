from .workplaces import Sector, Transactions
from .person import person
from .virus import Virus
from .lockdown import lockdown
import random
import numpy as np
import pandas as pd
import copy
class popdist(object):
	def __init__(self, Population_groups, Population_Dist, Population, sample=False):
		"""Initialized Population Distribution object

		Args:
			pm (object): Parameters object inheriting Population_groups, Population_Dist,Population
			sample (bool, optional): Whether we wish to sample age. Defaults to False.
		"""
		super(popdist, self).__init__()
		# These properties are constant throughout exectuion hence doesn't matter 
		self.PopGroup  		= Population_groups
		self.AgeGroupDist 	= Population_Dist # Between Classes
		self.Population 	= Population 

		self.AgeGroupLT    	= None
		self.AgeGroups 		= None
		self.Ages 			= None
		if sample:
			self.sampleage()

	def update_params(self,params_dict):
		'''
		AgeGroupDist 	list of length (number of Age Groups) indicating distribution
		Population 		int indicating population
		PopGroup 		list indicating maximum of different age groups
		
		Generated Params
		AgeGroupLT 		list2D lookup table generated using PopGroup
		AgeGroups 		list, list of AgeGroups of individual Citizens
		Ages 			list, list of Ages of individual Citizens
		'''
		for i in params_dict.items():
			setattr(self,i[0],i[1])

	def sampleage(self):
		"""Sample numerical age of the population
		"""
		temp 			= [0] + self.PopGroup 
		#LookupTable		 									
		self.AgeGroupLT 	= [[temp[i]+1,temp[i+1]] for i in range(len(self.PopGroup))]
		self.AgeGroups 		= random.choices(range(0,len(self.AgeGroupDist)),weights=self.AgeGroupDist,k=self.Population)
		self.Ages 		= list(map(lambda x: random.choice(range(self.AgeGroupLT[x][0],self.AgeGroupLT[x][1])), self.AgeGroups))

	def getage(self,Id:int):
		"""Returns the age given the ID of the person

		Args:
			Id (int): Index Id of the person. If its String ID Number after '_' is Id, for Int ID use number after 4th digit

		Returns:
			Int: Age of the requested Index Id
		"""
		return self.Ages[Id]

	def getageclass(self,Id:int):
		"""Returns the age Class given the ID of the person

		Args:
			Id (int): Index Id of the person. If its String ID Number after '_' is Id, for Int ID use number after 4th digit

		Returns:
			Int: AgeClass of the requested Index Id
		"""
		return self.AgeGroups[Id]


class city(Virus,lockdown,Transactions):
	def __init__(self,pm):
		
		self.pm             = pm
		self.SectorHolder   = {}
		self.Citizens       = [0]*pm.Population
		self.Families 		= []
		self.EmployedPop    = 0
		self.AgeDist 		= popdist(pm.Population_groups, pm.Population_Dist, pm.Population, sample=True)
		self.VirusC 		= 0
		self.Today 			= 0
		self.CityTestingCap = 0
		self.ComplianceRate = pm.ComplianceRate
		self.transmissionModes=pm.transmissionModes
		self.TodayShoppers  = set()
		super(city, self).__init__(pm)
	def initialize(self):
		self.__init_workplaces__()
		self.__init_citizens__()
		self.__initialize_families__()
	
	def __init_workplaces__(self):
		for sector in self.pm.sectors:
			Param = self.pm.Workplace_Params[sector]
			print(Param)
			Sec       = Sector((Param["T"],Param["E"],Param["V"]),self,sector)
			self.SectorHolder[sector] = Sec

			Sec.print_about()

	def __init_citizens__(self,start_index=0):
		ages 		= self.AgeDist.Ages[start_index:start_index+self.pm.Population]
		agegrp 		= self.AgeDist.AgeGroups[start_index:start_index+self.pm.Population]
		take_transport = random.choices([True, False], weights = [self.pm.Prob_use_TN, 1 -self.pm.Prob_use_TN],k=self.pm.Population)  
		for Id in range(start_index,start_index+self.pm.Population):
			self.Citizens[Id] = person(Id,self.pm,ages[Id],agegrp[Id],self,assign_work=True)

	def __initialize_families__(self,start_index=0):
		pop 					= self.pm.Population
		EFamilyMembers 			= self.pm.Family_size[0] #Get Param
		VarFamilyMembers 		= self.pm.Family_size[1] #Get Param
		membersaray 			= np.random.normal(loc=EFamilyMembers,scale=VarFamilyMembers*self.pm.RF,size=int(self.pm.Population/(EFamilyMembers-1)))  
		membersaray 			= np.round(membersaray).astype(np.int)
		
		citizenslist 			= self.Citizens#list(self.Citizens.values())

		family_number = 0
		pop_accounted = 0
		while pop_accounted<pop:
			members = membersaray[family_number]
			while members<=0:
				members = np.round((np.random.normal(loc=EFamilyMembers,scale=VarFamilyMembers*self.pm.RF))).astype(np.int)
			
			if pop_accounted+members>=pop:
				members = pop-pop_accounted
				
			familymembers = citizenslist[pop_accounted:pop_accounted+members]
			self.Families.append(familymembers)
			

			for member in familymembers:
				member.Family = family_number

			pop_accounted+=members
			family_number+=1
	def citizen_register(self):
		headers = ['ID','Family','Sector','SubClass','State','Status', 'Testing_State','Infected','Symptomatic','Recovered','Died']
		register = np.empty(shape=(self.pm.Population,len(headers)),dtype=object)
		for i, person_obj in enumerate(self.Citizens):
			obj = copy.copy(person_obj)
			register[i] = [obj.Id,obj.Family,obj.Work['Sector'],obj.Work['SubClass'], obj.State,obj.Status,obj.state,obj.History['Infected'],obj.History['Symptomatic'],obj.History['Recovered'],obj.History['Died']]
		return pd.DataFrame(register,columns=headers)