import numpy as np
import random

from tabulate import tabulate
class Workplace(object):
	def __init__(self,SectorName,Subclass,Id,E,V,Sector):
		super(Workplace, self).__init__()
		self.SectorName			= SectorName
		self.Subclass 			= Subclass
		self.Id 				= Id
		self.E 	                = E
		self.V 		            = V
		self.Counter 			= 0
		self.Working 			= set()
		self.Visiting 			= []
		self.Sector 			= Sector

	def print_about(self,get=False):
		table = [["Region:",self.RegionName]
				,["Sector:",self.SectorName]
				,["Subclass:",self.Subclass]
				,["Id:",self.Id]
				,["Working:",self.Working]
				,["Visiting:",self.Visiting]
				,["Daily_Expectation:",self.Daily_Expectation]
				,["Location:",hex(id(self))]
		]

		if get==False:
			print(tabulate(table), flush=True)
		else:
			return table
	'''
	def get_eff_contact_rate(self,c=1):
		return calibration.effective_contact_rate(self.Virus_Params["Time"],self.Virus_Params["Distance"],c)

	def get_id(self):
		return [self.RegionName,self.SectorName,self.Subclass,self.Id]
	'''

class Sector(object):
	def __init__(self, params,city=None,Name=None):
		super(Sector, self).__init__()
		self.T 		        = params[0] 
		self.E 	            = params[1]
		self.V 				= params[2]
		self.TSubClasses	= len(self.T)

		
		self.City 			= city
		self.Sec_Name		= Name
		self.WorkplacePlaceholder    = [{} for i in range(self.TSubClasses)] #we can name subclass as well
		self.IndexHolder 	= []

		self.NWorkers 		= np.zeros(self.TSubClasses,dtype=int)
		self.NWorkplaces    = np.zeros(self.TSubClasses,dtype=int)

		self.initialize_workplaces()

	def PeopleInSector(self):
		return sum(self.NWorkers)

	# @staticmethod
	def initialize_workplaces(self):        
		Id = 0
		self.IndexHolder.append(Id)
		for subclass in range(self.TSubClasses):
			self.NWorkplaces[subclass] = np.round(np.random.normal(self.T[subclass],self.T[subclass]/6*0)).astype(np.int)			
			
			for workplace in range(np.sum(self.NWorkplaces[:subclass]),np.sum(self.NWorkplaces[:(subclass+1)])):
				new_workplace = Workplace(self.Sec_Name,subclass,workplace,self.E[subclass],self.V[subclass], self)

				self.WorkplacePlaceholder[subclass][workplace]=new_workplace
				Id+=1 

			self.IndexHolder.append(Id)
		if(Id==0):
			self.WorkplacePlaceholder[0][0]=Workplace(self.Sec_Name, 0,0,self.E[0],self.V[0], self)
			self.NWorkplaces[0] +=1
			Id+=1 
			self.IndexHolder.append(Id) 
		else:
			self.IndexHolder.append(Id)

	def print_about(self,get=False):
		table = [["Name:",			self.Sec_Name]
				,["NWorkplaces:",	self.NWorkplaces]
				,["NWorkers:",		self.NWorkers]
				,["Param:",			(self.T,self.E,self.V )]
				,["Location:",hex(id(self))]
		]

		if get==False:
			print("Sector Information:\n",tabulate(table), flush=True,sep='')
		else:
			return table

	def update_values(self):
		for subclass in range(self.Total_SubClasses):
			for workplace in range(sum(self.Number_Workplaces[:subclass]),sum(self.Number_Workplaces[:(subclass+1)])):
				self.PeopleInSubClasses[subclass]+= self.WorkplacePlaceholder[subclass][workplace].Counter.value	
	'''
	def get_eff_contact(self):
		Sum = 0
		for subclass in range(self.Total_SubClasses):
			Sum += (self.PeopleInSubClasses[subclass]/self.PeopleInSector())*self.get_eff_contact_rate(subclass)*self.Daily_People_Expectation(subclass)
		return Sum
	
	def get_eff_contact_rate(self,subclass,c=1):
		return 


		.effective_contact_rate(self.Virus_Params[subclass]["Time"],self.Virus_Params[subclass]["Distance"],const=c)
	'''
class Healthcare(Sector):
	def __init__(self, params,Region=None,ReduceFactor=None):

		self.ReduceFactor = ReduceFactor

		super().__init__(params[0],Region=Region,Name="Healthcare", ReduceFactor=self.ReduceFactor)
		# All elements are constant.
		self.Types = ['Care_Center', 'Health_Center', 'Hospital']
		self.Capacity = {}

		self.Factor  = params[1]

		self.update_capacity()

	def update_capacity(self):
		for i in range(len(self.Number_Expectation)):
			self.Capacity[self.Types[i]] = self.Factor['Healthcare'][self.Region]*self.PeopleInSubClasses[i]

class Transactions(object):
	'''A Class performing day to day transactions. Inherited by region
	'''
	def __init__(self, pm):
		pass

	def daily_transactions(self):
		num_families = len(self.Families) #change this to freeFamilies later 		
		shoppingFamilies = np.random.randint(0, num_families, size=int(num_families*self.ProbablityOfPurchase))

		for i in shoppingFamilies:
			if len(self.Families[i])==0:
				continue

			shopper = random.choice(self.Region.Families[i])

			#Choose class 
			weights = [num_plc*num_peop for num_plc, num_peop  in zip(self.Workplaces['Commerce'].Number_Expectation, self.Workplaces['Commerce'].Daily_People_Expectation)]
			subclass = int(random.choices(list(range(0, len(self.Workplaces['Commerce'].Number_Expectation))), weights=weights)[0])
			id = random.choice(list(self.Workplaces['Commerce'].WorkplacePlaceholder[subclass].keys()))
			
			try:
				shoppingPlace = self.Workplaces['Commerce'].WorkplacePlaceholder[subclass][id]
			except:
				print(id)
				print(self.Workplaces['Commerce'].WorkplacePlaceholder)
				print(self.Workplaces['Commerce'].Number_Workplaces)				
				raise

			shoppingPlace.Visiting.append(shopper.IntID)
			shopper.GroceryPlace = shoppingPlace
			self.todayShoppers.append(shopper)

			#print('Person {} of region {} shops at {}'.format(shopper.IntID, self.Name, shoppingPlace))

	def clear_transactions(self):
		for subclass in range(len(self.Workplaces['Commerce'].Number_Expectation)):
			for workplace in self.Workplaces['Commerce'].WorkplacePlaceholder[subclass]:
				self.Workplaces['Commerce'].WorkplacePlaceholder[subclass][workplace].Visiting = []

		for shopper in self.todayShoppers:
			shopper.GroceryPlace = None

