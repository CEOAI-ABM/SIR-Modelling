import ctypes
import random
import numpy as np

from tabulate import tabulate
from transitions import Machine

# from .utils import strid_to_intid
from .contact_tracing import ContactTracing
from .statemachine import AgentStatusA, AgentStateA,TestingState

class person(AgentStateA,TestingState,ContactTracing): 
	"""Class for declaring person object
	Takes in 3 params and 2 optional params
	Id: Id of the person
	Age and age class
	1st Optional param is the city in which the person belongs and 2nd is that whether work has to be assigned
	"""
	def __init__(self, Id, pm=None, age=-1, ageclass=-1,  City=None, assign_work=False, isAlien=False):
		super(person, self).__init__()
		self.Id 			= Id
		self.pm 			= pm # Done because IT is very intertwined
		self.Age			= age
		self.AgeClass 		= ageclass
		self.Family 		= None
		self.FamilyCluster 	= None
		self.isAlien 		= isAlien
		self.City           = City
		self.GroceryPlace 	= None 

		self.spreadsTo		= {mode: [] for mode in pm.transmissionModes} if pm is not None else {}

		#self.TravelledIn 	= {
		#					'To_Work' : None,
		#					'To_Home' : None
		#					}
		
		self.useTN 			= False #By default doesn't use transport
		
		self.Work 			= {
							'Sector' 	: None,
							'SubClass' 	: None,
							'Id' 		: None, #Id of the Workplace
							}
		
		if City!= None:
			self.update_objects(self.City)
		
		self.VisitingPlaces = {
		'Commerce' 			: None,
		'Random' 			: None
		}
		self.ReproNumber 	= 0
		self.Disease 		= []

		if pm!=None:
			self.__get_disease__(pm.Comorbidty_matrix)

		self.PrintHeaders 	= ["Id","Age","RegionName","Family","Work","VisitingPlaces","Disease","State","Status"]
		
		if assign_work==True and pm!=None:
			self.assign_work(pm)

	def __repr__(self):
		return str(self.Id)

	def get_workplace(self):
		workplace = self.Work.copy()
		return workplace

	def __get_disease__(self,CM):
		for i in CM.items(): #Cm is comorbidity matrix
			probablity = [i[1][self.AgeClass],1-i[1][self.AgeClass]]
			has_disease = random.choices([True, False],weights=probablity)[0]
			if has_disease:
				self.Disease.append(i[0])

	def get_prob_severity(self,ProbSeverity):
		for i in self.Disease:
			ProbSeverity = ProbSeverity
		return ProbSeverity

	def get_death_rate(self,deafaultDR):
		for i in self.Disease:
			deafaultDR = deafaultDR
		return deafaultDR

	def get_workplace_obj(self, master=None):
		return self.City.SectorHolder[self.Work['Sector']].WorkplacePlaceholder[self.Work['SubClass']][self.Work['Id']]

	def get_workers(self,abc=None):
		return self.get_workplace_obj().Working 
	
	def traceme(self,master):
		self.print_about()
		
		Working = self.get_workers()
		if Working != None:
			print("Coworkers:")
			k = []
			for i in Working:
				k.append(self.City.Citizens[i].get_about())
			print(tabulate(k, headers=self.PrintHeaders))
		else:
			print("Jobless")
			
	def get_about(self):
		return [self.Id,self.Age,self.RegionName,self.Family,self.Work,self.VisitingPlaces,self.Disease,self.State,self.Status]


	def print_about(self,printwhat= None,get=False):
		if printwhat == None:
			printwhat = [self.get_about()]
		if get==False:
			print(tabulate(printwhat, headers=self.PrintHeaders))
		else:
			return tabulate(printwhat, headers=self.PrintHeaders)

	def __probablistically_assign__(self,probablity:list,pm):
		"""__probablistically_assign__ 
		Probablistically assigns a Sector, Region, Subclass and Workplace  

		Args:
			probablity (list(int)): Indicating Probablities of which sector work in an ordered fashion
			pm (object): Parameters Object of the parameters
			master (object, optional): Master Class Object. Defaults to None.
		"""
		sectors_temp = pm.sectors.copy()
		sectors_temp.append(None)
		tempsector = random.choices(sectors_temp,weights=probablity)[0]
		self.Work['Sector'] = tempsector

		if tempsector != None:
			self.City.EmployedPop += 1
		else:
			return
		
		model =self.City.SectorHolder[self.Work['Sector']]

		# <---------SubClass assignment ------->
		weights = []
		weights = list(np.multiply(model.NWorkplaces,model.E))

		self.Work['SubClass'] = int(random.choices(range(model.TSubClasses),weights=weights)[0])

		self.Work['Id'] = random.choice(list(model.WorkplacePlaceholder[self.Work['SubClass']].keys()))  
		#print('Person {} aquired lock'.format(self.IntID))
		obj 	= model.WorkplacePlaceholder[self.Work['SubClass']][self.Work['Id']]
		obj.Working.add(self)
		obj.Counter +=1
		model.NWorkers[self.Work['SubClass']] +=1
				
			
	def assign_work(self,pm):
		# Currently based on government data of Bhopal
		Age = 	 self.Age
		for i in pm.Population_groups:
			if(Age<=i):
				probablity = pm.Employment_params[i]
				break
		self.__probablistically_assign__(probablity,pm)

	def assign_route(self,Regions):
		source 	= self.RegionName 
		dest 	= self.Work['Region']
		if dest == None or dest == source:
			Regions.remove(source)
			dest = random.sample(Regions,k=1)[0]
			self.VisitingPlaces['Random'] = dest
		# reverse travel (dest to source) also considered
		self.useTN = True
		#For a rare bug

		k = 0
		while(1):
			try:
				if k==50:#If tried 50 times leave it
					break
				k+=1
				self.RouteTaken = random.sample(self.master.RouteLookup[frozenset([source, dest])], k=1)[0]
				obj = self.master.Routes[self.RouteTaken]
				obj.Lock.acquire()
				obj.Travellers[obj.Travellers_counter.value] = self.IntID
				obj.Travellers_counter.value += 1 
				obj.Lock.release()
				break
			except:
				obj.Lock.release()
				continue

		#print('Person {} travelling between {} and {} assigned to route {}. Others in route {}'.format(self.IntID, source, dest, self.RouteTaken, len(self.master.Routes[self.RouteTaken].Travellers[:self.master.Routes[self.RouteTaken].Travellers_counter.value])))
		#print()
