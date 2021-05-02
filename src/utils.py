from .calibration import sector_proportions
import timeit
import math
import numpy as np

def timeprinter(tym):
	a0 = tym.pop(0)
	print("Start Time:",a0[2])
	for i in range(len(tym)):
		a1=tym.pop(0)
		print("I:",a1[0],"-",a0[0],"\tTime:",a1[1]-a0[1])
		a0 = a1
	print("End Time:",a0[2])

class timecalc(object):
	def __init__(self):
		super().__init__()
		# timeit.time.clock()
		self.tym = []
		self.counter = 0
	
	def add_checkpoint(self,print_what=None):
		if print_what == None:
			print_what=self.counter
		self.tym.append([self.counter,timeit.time.time(),timeit.time.ctime()])
		self.counter +=1
	
	def print_result(self,tym=None):
		if tym==None:
			timeprinter(self.tym)
def get_Numbers(pm):
	sec_prop = sector_proportions(pm)
	for sector in pm.sectors:
		pop = int(sec_prop[sector]*pm.Population)
		pm.Workplace_Params[sector]["T"] = list(map(lambda x,y: max(int((pop*x)//y),1),pm.Workplace_Params[sector]["N"],pm.Workplace_Params[sector]["E"] ))
	return pm.Workplace_Params
def random_suspectibles(Density:float,Population:int,ComplianceRate:float):
	"""random_suspectibles Returns the number of Suspectile people for random Transmission

	Args:
		Density (float): density of the population
		Population (int): count of population
		ComplianceRate (float): Rate at which people obey orders, i.e entropy. Ranges between 0 to 1

	Returns:
		int: Number of Suspectible people 
	"""
	#print(ComplianceRate)
	Const 			= 4*math.pi*Density
	suspectibles 	= Const*((Population/Const)**(1-ComplianceRate))
	return int(suspectibles)
