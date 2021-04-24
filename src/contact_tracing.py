import ctypes
import random
import numpy as np

from functools import partial


class ContactTracing(object): 

	"""
	Contact Tracing class to analyze contacts of a person
	"""
	
	def __init__(self): 
		super().__init__()

	def __trace_workplace_contacts__(self,param:float):
		"""Trace the contacts from workplace

		Args:
			param (float): % of contacts actually remembered

		Returns:
			list: list of contacts, empty list if no contact 
		"""
		#Check if person is working
		if self.Work['Region'] != None:
			#Working people
			coworkers = self.get_workers(master=self.master) # Get Cowokers

			#Select number of coworkers as contact based on distribution and bound 0< <coworker
			num_work_contacts 	= int(max(min(np.random.normal(len(coworkers)/2,len(coworkers)/3), len(coworkers)), 0))
			#Select contact Randomly
			contacts 			= random.sample(coworkers, k=num_work_contacts)
			#Select Contacts whom we actually spread and add it to original List
			contacts 			+= self.spreadsTo[self.Work['Sector']]
			#Sample from them, parameterized 
			contacts 			= random.sample(contacts,k=int(param*len(contacts)))
			#Remove Duplicates
			contacts 			= list(dict.fromkeys(contacts))
			
			return contacts  

		else:
			#Not Working
			return []
			
	def __trace_family_contacts__(self): 
		"""Traces the family Contacts

		Returns:
			list: Entire family list if have a family else empty list
		"""
		if self.Family != None:
			return self.Families[self.Family]

		else:
			return []

	def __trace_grocery_contacts__(self): #TODO after grocery is restarted
		"""Traces the grocery Contacts
		NON FUNCTIONAL
		Returns:
			list: grocery contacts if have a grocery else empty list
		"""
		return []
	
	def __trace_transport_contacts__(self,param:float): 
		"""Traces the transport Contacts
		
		Returns:
			Sample of people from person's transport route    
		"""
		if self.useTN:
			#Number of Covtravellers
			total_co_travellors = self.master.Routes[self.RouteTaken].Travellers_counter.value
			#Expected people per bus
			expected_people 	= self.master.TAExpectedPeople
			#Number of days of contact tracing done
			days_to_consider 	= 14
			#Obtain people list
			people_in_route 	= self.master.Routes[self.RouteTaken].Travellers[:total_co_travellors]
			
			number_of_contacts 	= min(days_to_consider*expected_people, len(people_in_route))
			
			contacts 			= random.choices(people_in_route, k=number_of_contacts) 
			contacts 			+= self.spreadsTo['Transport']
			#Sample from them, parameterized 
			contacts 			= random.sample(contacts,k=int(param*len(contacts)))
			#Remove Duplicates
			contacts 			= list(dict.fromkeys(contacts ))

			return contacts

		else:
			return []

	def __transfer_to_home_region__(self, contacts_list):
		"""Summary
		
		Args:
			contacts_list (list of IntIDs or people objects): people who are to be added to shared list 
		"""
		for contact in contacts_list:
			contact_id 		= contact.ID

			self.put_to_test(self,"Contact")

	def trace_contacts(self):
		"""Summary
			Main function that calls tracing functions to get the contacts then adds them to the shared list of respective region
		"""
		contacts = []
		
		contacts += self.__trace_workplace_contacts__(param=self.Region.CT_Efficacy_Workplace)
		contacts += self.__trace_family_contacts__()
		#contact += self.__trace_grocery_contacts__()
		contacts += self.__trace_transport_contacts__(param=self.Region.CT_Efficacy_Transport)

		#print('Number of contacts traced of person {} = {}'.format(self.Id, len(contacts)))

		self.__transfer_to_home_region__(contacts)

class Testing(object):
	"""Summary
	
	Attributes:
		TestedP (TYPE): Description
		testingList (TYPE): Description
		testingList_counter (TYPE): Description
		testingStack (list): Description
	"""
	
	def __init__(self,pm):
		"""Testing Class to test people, this signifies government data. 
			testingList contains the people who have to be added to the testingStack. testingStack contains the people who are going to be tested in FIFO order
		"""
		super(Testing, self).__init__(pm)
		
		# Hospitalized when show symtoms but not tested
		# Quarentined when a contact

		self.TestingQueue 	= [] 

		self.NumTestedPositive = 0
		self.PTR 			= 0
		
		self.TestedP = {
		'Positive'	: {},
		'Negative' 	: {}
		}

	def __fresh_test__(self, person):
		"""
		Testing Rules for person who shows symptoms. Kept as a seperate function so that different rules can be applied to
		symptomatic people and traced people.

		Args:
			person (person class object): person to be tested
		"""
		#Rule 1: People with severe symptoms or people in Hospital or ICU
		if person.is_ICU() or person.is_Hospitalized():
			person.awaiting_test()

		#Rule 2: Symptomatic people who are above 60 or have comorbidities
		elif (person.Age >= 60) or (len(person.Disease) != 0):
			person.awaiting_test()

		#Rule 3: Symptomatic frontline workers (only healthcare for now, add police later)
		elif person.Work['Sector'] in ['Healthcare']: #Add police and other frontline workers as they are added
			person.awaiting_test()

	def __traced_contact_test__(self, person):
		"""
		Testing Rules for person who has been traced from a confirmed case. Kept as a seperate function so that 
		different rules can be applied to symptomatic people and traced people. Keeping rules same for now but can 
		be changed later. 

		Args:
			person (person class object): person to be tested
		"""
		#Rule 1: People with severe symptoms or people in Hospital or ICU
		if person.is_ICU() or person.is_Hospitalized():
			person.awaiting_test()

		#Rule 2: Symptomatic people who are above 60 or have comorbidities
		elif (person.Age >= 60) or (len(person.Disease) != 0):
			person.awaiting_test()

		#Rule 3: Symptomatic frontline workers (only healthcare for now, add police later)
		elif person.Work['Sector'] in ['Healthcare']: #Add police and other frontline workers as they are added
			person.awaiting_test()

	def put_to_test(self, person, Type):
		"""put_to_test 
		The testing protocol of the country, checks person state and test

		Args:
			person (obj): Person Object
			Type (str): Either "Fresh" or "Contact", both have different set of Rules.
		"""
		if person.isAlien == True:
			return

		if person.state == 'Not_tested' or person.state == 'Tested_Negative':
			if Type == "Fresh":
				self.__fresh_test__(person)
				
			elif Type == "Contact":
				self.__traced_contact_test__(person)

	def test_person(self, person, trace=None, PrivateTest=False): 
		"""Summary
		
		Args:
			person (TYPE): Description
			trace (bool, optional): Description
		"""
		if trace == None:
			trace = self.TracingOn

		if person.is_Healthy() or person.is_Recovered():
			person.tested_negative(PrivateTest)
			return 'Negative'
		else:
			person.tested_positive(PrivateTest)
			if trace:
				person.trace_contacts() 

			return 'Positive'


	def update_city_testing_cap(self, master):
		"""
		This function is for increasing CityTestingCap
		Args:
		    master (object): master object
		"""
		# print('On day {}, master.CityTestingCap = {}'.format(self.Today, master.CityTestingCap.value))
		self.CityTestingCap = self.pm.TestingCapSeries[self.Today]
		
	def __update_ptr__(self, NumPositives, NumTests):
		"""
		Update PTR after conducting tests
		"""
		self.PTR = NumPositives/NumTests

	def daily_testing(self):
		"""Summary
			FIFO testing stack
		Returns:
			TYPE: Description
		"""
		
		if self.PTR != 0:
			PublicTestingCap = (0.05/self.PTR)*self.CityTestingCap
		else:
			PublicTestingCap = self.CityTestingCap
		
		MaxTests 	= len(self.TestingQueue) # Max Number of tests that need to be conducted today
		NumTests 	= np.round(min(MaxTests, PublicTestingCap)).astype(int)
		NumPositives = 0
		NumPrivate 	= self.CityTestingCap - NumTests
		
		#print('Region {} MaxTests = {}, NumTests = {} on day {}'.format(self.Name, MaxTests, NumTests, self.Today))
		
		if NumTests == 0:
			return 
		for person_obj in self.TestingQueue[:NumTests]:
			if person_obj.state == 'Awaiting_Testing':
				TestingResult = self.test_person(person_obj,self.TracingOn)
				if TestingResult == 'Positive':
					NumPositives += 1
		
		self.__update_ptr__(NumPositives, NumTests)								
		self.daily_private_testing( NumPrivate)
	
	def daily_private_testing(self, NumPrivate):
		"""
		Private testing. Kept as a seperate function so that it can be turned on or off independently.
		People are randomly sampled and tested. No stack, only the people who are to be tested are sampled. 
		Proportion of people to be tested privately by each region is kept same as public, 
		"""

		if NumPrivate == 0:
			return
			

		todayTestedPrivate = random.sample(self.Citizens, k=NumPrivate) 

		for i, person_obj in enumerate(todayTestedPrivate):			
			if person_obj.state != 'Tested_Positive':
				person_obj.awaiting_test(PrivateTest=True)
				self.test_person(person_obj, self.TracingOn, PrivateTest=True) 
			
			#if i == PrivateTestingCap:
			#	break

if __name__ == '__main__':
	cg = ContactTracing()				
