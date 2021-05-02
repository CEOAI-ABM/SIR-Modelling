import transitions
from functools import partial
# from transitions import transitions.Machine


# TODO: whenever there is a state chage store the following
# (DAY,function_called) -> Stored for every person for agent status, state and Testing state
class AgentStatusA(object):
	"""The Statemachine of the agent"""
	status  = ['Free','Quarentined','Out_of_city','Hospitalized','ICU','Isolation']

	def __init__(self):
		"""Agent Status class is responsible for figuring out the Mobility of the agent, the agent mobility can be
		'Free','Quarentined','Out_of_city','Hospitalized','ICU','Isolation'
		"""
		super(AgentStatusA, self).__init__()
		self.ADDED_BIT 				= True
		self.TruthStatus 			= None
		self.Last_Added_Placeholder = None
		self.buffer = []

		self.Status 				= self.status[0]	

	# def log_update(self,message):

	def update_objects(self,TruthStatus):
		"""Update object of Virusmodel

		Args:
			TruthStatus (object): Truth State object to update
		"""
		self.TruthStatus 		= TruthStatus

	def __remove_from_transport__(self):
		if self.useTN == True:
			self.City.TravellingCitizens.remove(self)

			#print('Person {} removed from travelling list of City {}. New length = {}'.format(self.IntID, self.City.Name, len(self.City.TravellingCitizens)))

	def _remove_(self):
		"""Remove from workplace and transport list
		"""
		if self.ADDED_BIT:
			obj = self.get_workplace_obj()
			if obj !=None:
				self.buffer.append('_remove_')
				obj.Working.remove(self) 
			self.ADDED_BIT = False
			
			self.__remove_from_transport__()

	def _add_(self):
		"""Add to workplace and transport list
		"""
		if ~self.ADDED_BIT:
			obj = self.get_workplace_obj()
			if obj != None:
				if obj.Working!=None:
					self.buffer.append('_add_')
					obj.Working.add(self) 
				self.ADDED_BIT = True
			
			if self.useTN == True:
				self.City.TravellingCitizens.add(self)
			
	
	def _left_(self):
		"""Leave city, calls remove
		"""
		self._remove_()

	def _entered_(self):
		"""Come back to city
		"""
		self._add_()
		

	def __remove_from_placeholder__(self):
		"""Remove the person from the Truth Status Placeholders

		Returns:
			bool: Whether Removed or not
		"""
		try:
			if self.Last_Added_Placeholder == 0:  # If he is AFreeP
				self.TruthStatus.AFreeP.remove(self)
				return True
			elif self.Last_Added_Placeholder == 1:  # If he was Quarentined
				self.TruthStatus.AQuarentinedP.remove(self)
				return True
			elif self.Last_Added_Placeholder == 2:  # If he was Isolated
				self.TruthStatus.SIsolatedP.remove(self)
				return True
			elif self.Last_Added_Placeholder == 3:  # If he was Hospitalized
				self.TruthStatus.SHospitalizedP.remove(self)
				return True
			elif self.Last_Added_Placeholder == 4:  # If he was Icu
				self.TruthStatus.SIcuP.remove(self)
				return True
			else:
				return False
		except:
			self.about()
			raise

	def leave_city(self):
		acceptable_states	= [self.status[0]]
		try:
			assert self.Status in acceptable_states
		except:
			print('##########', self.Status)
			raise
		self.Status  		= self.status[2]
		self._left_()

		self.__remove_from_placeholder__()
		self.Last_Added_Placeholder = None

	def enter_city(self):
		acceptable_states	= [self.status[2]]
		try:
			assert self.Status in acceptable_states
		except:
			print('##########', self.Status)
			raise
		self.Status  		= self.status[0]
		self._entered_()
		if self.is_Asymptomatic():
			self.TruthStatus.AFreeP.add(self)
			self.Last_Added_Placeholder = 0

	def quarentined(self,DAY):
		acceptable_states	= [self.status[0],self.status[1],self.status[2]]
		assert self.Status in acceptable_states
		
		if self.Last_Added_Placeholder != 1:
			self.__remove_from_placeholder__()

		if self.is_Free():	# If free add to quarentined placeholders
			self.TruthStatus.AQuarentinedP.add(self)
			self.Last_Added_Placeholder = 1 

		
		self.Status  		= self.status[1]
		self._remove_()

	def hospitalized(self,DAY):
		acceptable_states	= [self.status[0],self.status[1]]
		assert self.Status in acceptable_states
		self.Status  		= self.status[3]
		self._remove_()

		self.show_symptoms(DAY)

		if self.__remove_from_placeholder__(): #If person is in city and removal is successful
			self.TruthStatus.SHospitalizedP.add(self)
			self.Last_Added_Placeholder = 3

	def admit_icu(self,DAY):
		acceptable_states	= [self.status[0],self.status[1],self.status[3]]
		assert self.Status in acceptable_states
		self.Status  		= self.status[4]
		self._remove_()

		self.show_symptoms(DAY)

		if self.__remove_from_placeholder__(): #If person is in city and removal is successful
			self.TruthStatus.SIcuP.add(self)
			self.Last_Added_Placeholder = 4

	def isolate(self,Today):
		acceptable_states	= [self.status[0],self.status[1],self.status[3],self.status[4],self.status[5]]
		assert self.Status in acceptable_states
		
		if self.Status == self.status[0] or self.Status == self.status[1]:
			self.show_symptoms(Today)

		if self.Last_Added_Placeholder != 2:
			if self.__remove_from_placeholder__(): #If person is in city and removal is successful
				self.TruthStatus.SIsolatedP.add(self)
				self.Last_Added_Placeholder = 2


		self.Status  	= self.status[5]
		self._remove_()

	def is_Free(self):
		return self.Status == self.status[0]
	def is_Quarentined(self):
		return self.Status == self.status[1]
	def is_Out_of_City(self):
		return self.Status == self.status[2]
	def is_Hospitalized(self):
		return self.Status == self.status[3]
	def is_ICU(self):
		return self.Status == self.status[4]
	def is_Isolation(self):
		return self.Status == self.status[5]

class AgentStateA(AgentStatusA):
	states  = ['Healthy','Asymptomatic','Symptomatic','Recovered','Died']

	def __init__(self):
		"""Agent status is the status of person with respect ot the virus
		"""
		super(AgentStateA, self).__init__()
		#self 				= person
		self.State 			= self.states[0]
		self.TruthStatus 	= None
		
	def infected(self,DAY):
		acceptable_states	= [self.states[0]]
		assert self.State in acceptable_states
		self.State  		= self.states[1]

		self.TruthStatus.AFreeP.add(self)

		self.Last_Added_Placeholder = 0
		self.History["Infected"] = DAY

	def show_symptoms(self,DAY):
		acceptable_states	= [self.states[1],self.states[2]]
		assert self.State in acceptable_states
		self.State  		= self.states[2]
		self.History["Symptomatic"] = DAY


	def recover(self,DAY):
		acceptable_states	= [self.states[2]]
		assert self.State in acceptable_states
		self.State  		= self.states[3]
		self.Status   		= self.status[5]
		if self.__remove_from_placeholder__(): #Removal is succesful, mtlb seher me h
			self.TruthStatus.RRecoveredP.add(self)
			self.Last_Added_Placeholder =5 
		self.History["Recovered"] = DAY
		self.History["Died"] 	  = -1

	def die(self,DAY):
		acceptable_states	= [self.states[2]]
		assert self.State in acceptable_states
		self.State  		= self.states[4]
		self.Status 		= self.status[5]
		if self.__remove_from_placeholder__(): #Removal is succesful, mtlb seher me h
			self.TruthStatus.RDiedP.add(self)
			self.Last_Added_Placeholder = 6 
		self.History["Recovered"] = -1
		self.History["Died"] 	  = DAY
		
	def is_Healthy(self):
		return self.State == self.states[0]
	def is_Asymptomatic(self):
		return self.State == self.states[1]
	def is_Symptomatic(self):
		return self.State == self.states[2]
	def is_Recovered(self):
		return self.State == self.states[3]
	def is_Died(self):
		return self.State == self.states[4]

class TestingState(object):
    
	"""Summary
	
	Attributes:
	    in_stack (bool): Description
	    machine (TYPE): Description
	    state (str): Description
	    tested (bool): Description
	"""
	
	machine = transitions.Machine(model=None, states=['Not_tested', 'Awaiting_Testing', 'Tested_Positive','Tested_Negative'], initial='Not_tested',
					  transitions=[
						  {'trigger': 'awaiting_test', 'source': ['Not_tested','Awaiting_Testing','Tested_Negative'], 'dest': 'Awaiting_Testing','before':'add_to_TestingQueue'},
						  {'trigger': 'tested_positive', 'source': 'Awaiting_Testing', 'dest': 'Tested_Positive','before':'tested_positive_func'},
						  {'trigger': 'tested_negative', 'source': 'Awaiting_Testing', 'dest': 'Tested_Negative','before':'tested_negative_func'},
					  ])
	def __init__(self): 
		"""This is responsible for updating testing state of the person
		
		Deleted Parameters:
		    person (object): Home object
		    VM (object): Virusmodel object
		"""
		super().__init__()
		self.state 		= 'Not_tested'
	def __remove_from_testing_list__(self): 
		self.City.TestingQueue.remove(self)

	def add_to_TestingQueue(self, PrivateTest=False): 
		"""Summary
		"""
		# This function is for the City to add citizens into testingQueue
		if PrivateTest == False:
			if self.state != 'Awaiting_Testing' :
				self.City.TestingQueue.append(self)
			if self.state == 'Tested_Negative':
				self.City.TestedP['Negative'].remove(self)

				#print('City {} added person {}'.format(self.City.Name, self.IntID))

	#pass type of test
	def tested_positive_func(self,Today, PrivateTest=False): 
		"""Summary
		"""
		self.City.TestedP['Positive'].add(self)
		self.City.NumTestedPositive += 1 

		if PrivateTest == False: 
			self.__remove_from_testing_list__()
		
		if self.is_Quarentined():
			self.isolate(Today)


	def tested_negative_func(self, PrivateTest=False):
		"""Summary
		"""
		self.City.TestedP['Negative'].add(self)

		if PrivateTest == False:
			self.__remove_from_testing_list__()

	

	def __getattribute__(self, item):
		"""Summary
		
		Args:
		    item (TYPE): Description
		
		Returns:
		    TYPE: Description
		"""
		try:
			return super(TestingState, self).__getattribute__(item)
		except AttributeError:
			if item in self.machine.events:
				return partial(self.machine.events[item].trigger, self)
			raise


	

		
