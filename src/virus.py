import random
import numpy as np

from tabulate import tabulate

from .calibration import get_TR
from .contact_tracing import Testing
# from .transport_sampled import Intercity_Transport
from .utils import  random_suspectibles

class TruthClassStatus(object):
	def __init__(self,pm):
		"""This signifies the truth of the data
		"""
		super(TruthClassStatus, self).__init__(pm)
		# self.arg = arg

		self.AFreeP 		= set()
		self.AQuarentinedP 	= set()
		self.SIsolatedP 	= set()
		self.SHospitalizedP = set()
		self.SIcuP 			= set()
		self.RRecoveredP 	= set()
		self.RDiedP 		= set()

	def print_status(self):
		table = [["Asymptomatic Free:",			len(self.AFreeP)]
				,["Asymptomatic Quarentined",	len(self.AQuarentinedP)]
				,["Symptomatic Isolated:",		len(self.SIsolatedP)]
				,["Symptomatic Hospitalized:",	len(self.SHospitalizedP)]
				,["Symptomatic ICU:",			len(self.SIcuP)]
				,["Results Recovered:",			len(self.RRecoveredP)]
				,["Results Died:",				len(self.RDiedP)]
				]
		return tabulate(table)

	def get_asymptomatic(self):
		return self.AFreeP + self.AQuarentinedP

	def get_symptomatic(self):
		return self.SIsolatedP+self.SHospitalizedP+self.SIcuP

	def get_results(self):
		return self.RRecoveredP + self.RDiedP

	def case_fatality_rate(self):
		return len(self.RDiedP)/len(self.get_results)

	def case_survivability_rate(self):
		return len(self.RRecoveredP)/len(self.get_results)

class Virus(TruthClassStatus, Testing):
	"""Virus class; Arguments is a list of parameters
	This class is to signify what truth is
	"""
	def __init__(self, pm):
		"""Class to spread virus

		Args:
			pm (object): paramters object containing Virus_PerDayDeathRate,.Virus_IncubationPeriod,Virus_ExpectedCureDays Virus_FullCapRatio,Virus_ProbSeverity,Virus_Prob_ContactTracing
			region (ojbect): Region Object of the region virus belongs
		"""
		super(Virus, self).__init__(pm)
		self.name 						= pm.Virus_Name 
		self.conn 						= None
		
		self.TR 						= None # Transmission Rate
		
		# Dr is death rates
		self.AgeDR 						= pm.Virus_PerDayDeathRate
		self.Esymptomstime				= pm.Virus_IncubationPeriod # or incubabtion time

		self.CureTime 					= pm.Virus_ExpectedCureDays
		self.FullCapRatio 		 		= pm.Virus_FullCapRatio

		self.PseudoSymptoms_Prob 		= pm.PseudoSymptoms_Prob
		self.ProbSeverity 				= pm.Virus_ProbSeverity 

		# Day wise placeholder
		self.Symptom_placeholder 		= [ set() for i in range(30) ]
		self.Recovers_Placeholder 		= [ set() for i in range(60) ]
		self.Deaths_Placeholder 		= [ set() for i in range(60) ]
		
		# self.Contact_List				= []
		self.DataTransferList 			= []
		self.numSpread					= {mode: [0]*(self.pm.SIMULATION_DAYS+2) for mode in pm.transmissionModes}

		self.RepoRateSum 				= 0
		self.Total 						= 0

		# Contact Tracing Efficacy
		self.CT_Efficacy_Workplace		= pm.CT_Efficacy_Workplace
		self.CT_Efficacy_Transport		= pm.CT_Efficacy_Transport
		self.EDays 						= np.average(self.Esymptomstime,weights=pm.Population_Dist)
	
	def update_params(self,params_dict):
		'''
		name 					String
		TR 						dict with sector: TR
		AgeDR 					list between different age groups
		Esymptomstime 			list between different age groups
		CureTime 				scalar
		MaxTestingCap			scalar
		FullCapRatio			list bw different subclass of hospitals
		Prob_ContactTracing 	scalar
		ProbSeverity 			matrix of size age groups x subclass of hospitals
		'''
		for i in params_dict.items():
			setattr(self,i[0],i[1])

	def updateratetransmissions(self,pm,ratestransmissions=None,c=None):
		"""Update Transmission Rates

		Args:
			pm (object): Paramters object
			ratestransmissions (dict, optional): if wish to enforce specific Tranmsision Rate. Defaults to None.
		"""
		self.VirusC = self.VirusC if c is None else c
		self.TR = get_TR(c=self.VirusC,pm1=pm) #VirusC is a property of City			

	def get_reproduction_rate(self):
		"""Calculates Reproduction rate which is RepoRateSum/Total people

		Returns:
			float: Rerporduction Rate
		"""
		return 0 if self.Total == 0 else self.RepoRateSum*self.EDays/self.Total

	def gets_virus(self, person):
		"""State change of a person from healthy to infected

		Args:
			person (person): person ojbect

		Returns:
			int: 0 if person wasn't able to infect due to already infected or out of Region. 1 otherwise
		"""
		if person.is_Out_of_City()==False:
			if person.is_Healthy() == True :
				Symptom  = int(np.random.normal(self.Esymptomstime[person.AgeClass],self.Esymptomstime[person.AgeClass]/3*self.pm.RF))
				Symptom  = max(0,Symptom)
				self.Symptom_placeholder[Symptom].add(person)
				person.infected(self.Today)
				self.RepoRateSum+=1
				return 1
			else:
				return 0
		else:
			return 0

	def spread_virus(self, person, TR:float, contactsList, mode, master):
		"""Spread virus at a particular Place to the contacts of specific person

		Args:
			person (object): person object from whom virus is spreading
			TR (float): Transmission Rate of spreading
			list_of_contacts (list of ints/objects): list of int ID's of the person in contact/list of person objects in contact at the place
			mode: (str) where the spread takes place ['Home', 'Transport', 'Work','Random']
			master (object): master object.
		""" 
		if len(contactsList) == 0 or TR==0:
			return		

		intlist = False

		n 			= len(contactsList)
		p 			= TR
		NumInfected = np.random.binomial(n,p)
		# print(n,p,NumInfected,mode)
		if NumInfected!=0:
			PeopleInfected = random.sample(contactsList, k=NumInfected)
			# print(PeopleInfected)
			for member_obj in PeopleInfected:
				if member_obj.isAlien: # Not adding LocalAliens for now
					continue 
				
				# home_region_locked = member_obj.Region.Locked.value
				# work_region_locked = master.Regions[member_obj.Work['Region']].Locked.value if member_obj.Work['Region'] != None else 0
				
				#Neither home region nor work region should be locked
				#But if mode is home then transmission will always take place
				# if (work_region_locked == 0 and home_region_locked == 0) or mode == 'Home' or mode == 'Random': 

				sector = member_obj.Work['Sector'] 
				if sector != None:
					sectorIndex = sector
					if master.SectorLockStatus[sectorIndex] == 0: # Sector should not be locked. 
						person.ReproNumber += self.gets_virus(member_obj)
						person.spreadsTo[mode].append(member_obj.Id)
						self.numSpread[mode][self.Today] += 1

				else: # Unemployed (if a person is working only then do we need to check the status of his sector)
					person.ReproNumber += self.gets_virus(member_obj)
					person.spreadsTo[mode].append(member_obj.Id)
					self.numSpread[mode][self.Today] += 1


	def apply_dr_multiplier(self, person, deathrate:float):
		"""Apply Death Rate multipler to a person' death rate based on his comobrbidity

		Args:
			person (object): Person ojbect
			deathrate (float): current deathrate

		Returns:
			float: new deathrate
		"""
		multiplier = 1
		try:
			if person.is_Isolation() and len(self.SIsolatedP) > self.Region.Workplaces['Healthcare'].Capacity['Care_Center']:
				multiplier = self.FullCapRatio[0]
	
			elif person.is_Hospitalized() and len(self.SHospitalizedP) > self.Workplaces['Healthcare'].Capacity['Health_Center']:
				multiplier = self.FullCapRatio[1]
			
			elif person.is_ICU() and len(self.SIcuP) > self.Region.Workplaces['Healthcare'].Capacity['Hospital']:
				multiplier = self.FullCapRatio[2]
		except:
			pass

		return deathrate*multiplier
											 
	def has_symptoms(self,person,cure:int):
		"""Subroutine to change the state of person to symptomatic

		Args:
			person (object): person object who has shown symptons
			cure (int): days after which the person would be cured
		"""
		if person.is_Out_of_City():
			person.quarentined()
			return
		prob_severity 	= person.get_prob_severity(self.ProbSeverity[person.AgeClass])
		deathrate 	 	= person.get_death_rate(self.AgeDR[person.AgeClass])
		deathrate 		= self.apply_dr_multiplier(person, deathrate)

		choice = random.choices([person.quarentined, person.hospitalized, person.admit_icu], weights=prob_severity)[0]
		choice(self.Today) 
		
		if person.is_Quarentined():
			person.show_symptoms(self.Today)

		if self.pm.TestingOn:
			self.put_to_test(person,"Fresh")
		
		if cure<0:
			cure = 0
		
		deathrate = self.apply_dr_multiplier(person,deathrate)
		deathday  = np.random.geometric(p=deathrate, size=1)[0]
		
		if cure<deathday:
			self.Recovers_Placeholder[cure].add(person)
		else:
			self.Deaths_Placeholder[deathday].add(person)
		
	def daily_symptoms_check(self):
		"""Checks for people whose symptoms have shown today. These people either will go to ICU,Hospital or remain at home
		"""
		today_symptoms = self.Symptom_placeholder.pop(0)

		#print('In region {}, {} people are added to testing list'.format(self.Name, len(today_symptoms)))
		curearray 	= np.random.normal(self.CureTime,self.CureTime/3*self.pm.RF,size=len(today_symptoms))
		for i,person in enumerate(today_symptoms):
			self.has_symptoms(person,int(curearray[i]))

	def daily_hospitals_check(self):
		"""Checks for all people who are supposed to be cured or died today i.e reach terminal state of statemachine
		"""
		today_cured = self.Recovers_Placeholder.pop(0)
		for person in today_cured:	
			person.recover(self.Today)

		today_died  = self.Deaths_Placeholder.pop(0)
		for person in today_died:	
			person.die(self.Today)

	def daily_pseudo_symptoms(self):
		"""
		Samples people at random to show pseudo symptoms (ILI but not Covid). Testing policy will be same as that for
		real person since it isn't known beforehand whether it is a Covid case or not
		"""
		if self.pm.TestingOn==False:
			return
		#today_pseudo_symptoms_idx = random.sample(list(self.Citizens), k=int(self.PseudoSymptoms_Prob*len(self.Citizens)))
		today_pseudo_symptoms = random.sample(self.Citizens, k=int(self.PseudoSymptoms_Prob*len(self.Citizens)))
		for person in today_pseudo_symptoms:
			#person = self.get_person_obj(Str_ID=self.get_strid(idx))

			if person.is_Hospitalized() or person.is_ICU() or person.state == 'Tested_Positive' or person.state == 'Awaiting_Testing':
				continue

			self.put_to_test(person, "Fresh")
			
	def check_infected_list(self, master):
		#print('Region {} on day {} InfectedList = {}'.format(self.Name, self.Today, self.InfectedList[:self.InfectedSize.value]))		

		for i in range(self.InfectedSize.value):
			if self.InfectedList[i] == 0:
				continue

			# WORKAROUND FOR ICT
			try:
				person_obj = self.get_person_obj(Int_ID=self.InfectedList[i])
			except:
				#print('Skipping person')
				continue
				raise

			home_region_locked = person_obj.Region.Locked.value
			work_region_locked = master.Regions[person_obj.Work['Region']].Locked.value if person_obj.Work['Region'] != None else 0	

			if work_region_locked == 0 and home_region_locked == 0:

				sector = person_obj.Work['Sector'] 
				if sector != None: 
					sectorIndex = sector
					if master.SectorLockStatus[sectorIndex] == 0: # Sector should not be locked. 
						self.__getattribute__("gets_virus")(person_obj)

				else:
					self.__getattribute__("gets_virus")(person_obj)
				
		self.InfectedSize.value = 0

	def __workplace_transmissions__(self, person_obj, master):
		sector = person_obj.Work['Sector']
				
		# Workaround to allow for police and other essential workers to continue working during lockdown
		if sector != 'Social':
			if sector == None or master.SectorLockStatus[sector]:
				return

		Coworkers = person_obj.get_workers()
		self.spread_virus(person_obj, self.TR[sector], Coworkers, sector, master)

	def __transport_transmissions__(self, person_obj, master):
		# person doesn't use transport or tranport is shutdown
		if person_obj.useTN == False or master.SectorLockStatus['Transport'] == 1:			return

		
		#  Containment zones in dest and source regions 
		if (master.Lockdown == True) :
			return

		assert person_obj.useTN == True

		route 			= master.Routes[person_obj.RouteTaken]
		PeopleInRoute 	= route.Travellers[:route.Travellers_counter.value]
		NumTravellers 	= master.TAExpectedPeople
		if NumTravellers>len(PeopleInRoute):
			NumTravellers = len(PeopleInRoute)
		Travellers 		= random.sample(PeopleInRoute, k=NumTravellers) 
		self.spread_virus(person_obj, self.TR['Transport'], Travellers, 'Transport', master)

	def __home_transmissions__(self, person_obj, master):
		sectorIndex = 'Home'
		
		if master.SectorLockStatus[sectorIndex] == 0: # Sector should not be locked
			
			Family 	= self.Families[person_obj.Family]
			self.spread_virus(person_obj, self.TR['Home'], Family, 'Home', master)

	def __transaction_transmissions__(self, person_obj, master):
		sectorIndex = 'Grocery'

		if master.SectorLockStatus[sectorIndex] == 0: # Sector should not be locked

			GroceryPlace  	= person_obj.GroceryPlace
			GroceryContacts = GroceryPlace.Visiting + GroceryPlace.Working[:GroceryPlace.Counter.value]
			self.spread_virus(person_obj, self.TR['Grocery'], GroceryContacts, 'Grocery', master=master)

	def __quarantine_transmissions__(self, person_obj, master):
		sectorIndex = 'HomeQuarantine'
		
		if master.SectorLockStatus[sectorIndex] == 0: # Sector should not be locked

			Family = self.Families[person_obj.Family]
			self.spread_virus(person_obj, self.TR['Home'], Family, 'HomeQuarantine', master)

	def __random_transmissions__(self, person_obj, master):
		if master.SectorLockStatus['Random'] == 1 or self.ComplianceRate == 1.0:
			return
		
		suspectibles 	= random_suspectibles(self.pm.Density,self.pm.Population,self.ComplianceRate)
		Regioners 		= random.sample(self.Citizens,k=suspectibles)	
		self.spread_virus(person_obj, self.TR['Random'], Regioners, 'Random', master)

	def daily_transmissions(self, master=None):
		"""Daily Transmission Control Sub-routing, this is the important subroutine which is responsible for spreading the virus in the city
		Args:
			master (object): master object
		"""

		self.daily_testing()
		self.daily_symptoms_check()
		self.daily_hospitals_check()
		self.daily_pseudo_symptoms()
		master=self
		temp_AFreeP 		= self.AFreeP.copy()
		temp_AQuarentinedP 	= self.AQuarentinedP.copy()
		self.Total = 0
		self.RepoRateSum = 0

		#Free People of this regions
		for person_obj in temp_AFreeP:
			self.Total +=1
			assert person_obj.is_Free() == True

			if person_obj.Work['Sector'] != None:
				self.__workplace_transmissions__(person_obj, master)

			if person_obj.useTN == True: 
				self.__transport_transmissions__(person_obj, master)

			if person_obj.Family != None:
				self.__home_transmissions__(person_obj, master)

			if person_obj.GroceryPlace != None:
				self.__transaction_transmissions__(person_obj, master)

			self.__random_transmissions__(person_obj, master)
		
		#People in home quarantine spreading it to their family members	
		
		for person_obj in temp_AQuarentinedP: 
			self.Total +=1
			
			if person_obj.Family != None:
				self.__home_transmissions__(person_obj, master)

			self.__random_transmissions__(person_obj, master)
			
		self.Symptom_placeholder.append(set())
		self.Deaths_Placeholder.append(set())
		self.Recovers_Placeholder.append(set())
