import numpy as np 
import math 
import statistics

from tabulate import tabulate

# from .parameters_shape import Parameters as Param
# pm = Param("Database/Kolkata/1_Ward_Population/Ward_300620.shp",'WardNo')
# Applicable for entire city
def distance_dist( pm1 ,distance,Dist=None):
	'''
	This function represents Distance wise Absoulte Risk Distribution of the corona virus 
	Inputs: 
	distance: float 
	Dist 	: dict having constant and ratio keys (optional)
	
	returns
	absolute risk: float 

	abs_risk = Constant / (distance*Ratio)
	Constant = Value of absolute risk < 1 m 
	Ratio  	 = Per m decrease in Risk
	'''
	if Dist == None:
		Param = pm1.Virus_DistanceDist.copy()
	else:
		Param = Dist

	if distance<1:
		return Param["Constant"]
	else:
		return Param["Constant"]/(distance*Param["Ratio"])

# Applicable for entire city
def effective_contact_rate(time,d,const,pm1):
	'''
	Effective Contact Rate is calculated as follows
	Beta(ECR) = gamma x p 
	gamma = total contacts = exposure time in hours x contacts per hour
	p 	  = probablity of tranmission per contact = absoulte risk(distance)
	'''
	def gamma(time,contacts_ph):
		return time*contacts_ph
	def p(distance):
		return distance_dist(pm1,distance)
	return gamma(time,const)*p(d)

def get_TR(pm1,c=1):
	"""returns the TR of different sectors

	Args:
		c (int, optional): 	Constant value of virus. Defaults to 1.
		pm1 (parameters object, optional): Parameters object. Defaults to pm.

	Returns:
		TR: Transmission Rate of different sectors
	"""	

	sectors 		= pm1.sectors.copy()
	Virus_Params 		= pm1.Virus_Params.copy()
	Workplace_Params	= pm1.Workplace_Params.copy()
	Mask_Fraction 		= pm1.Sector_Mask_Fraction.copy() # Fraction of the people in each sector who wear a mask.

	for sector in sectors:
		Param 	= Workplace_Params[sector]["V"]
		# Weights = np.multiply(Workplace_Params[sector+"_NumberOfSizei"],Workplace_Params[sector+"_ExpectedPeopleInSizei"])
		avg  	= np.average(Param,axis=0)
		Virus_Params[sector]={'Time':Param[0],'Distance':Param[1]}

	sectors += ['Home','Transport','Grocery','Unemployed','Random']
	TR 				= {}
	for sector in sectors:
		TR[sector] = effective_contact_rate(Virus_Params[sector]['Time'],Virus_Params[sector]['Distance']*Mask_Fraction[sector],c,pm1)
	
	#print('complicance rate', pm1.Initial_Compliance_Rate)	
	# print(TR)
	return TR
# Applicable for entire city
def sector_proportions(pm1,sector=None,RegionName=None ):
	'''
	sector Proportions(SP) is the Expected proportion of people employed in Different Sectors
	SP 		= sum(AgeDist[x]*Employment[x]) at y axis
	for all x in ageGroups
	'''
	sectors 		= pm1.sectors.copy()
	EmploymentDist 	= pm1.Employment_params.copy()
	AgeDist 		= pm1.Population_Dist.copy()
	AgeGroups 		= pm1.Population_groups.copy()
	ProblityPurchase = pm1.Transaction_ProbablityOfPurchase
	Family_size 	= pm1.Family_size.copy()[0]

	# Family_
	sectors.append('Unemployed')
	proportions = {'Home':1,'Transport':0,'Grocery':ProblityPurchase/Family_size}

	Prob_use_tran 	= pm1.Prob_use_TN
	# Family_
	sectors.append('Unemployed')
	proportions = {'Home':1,'Transport':Prob_use_tran,'Grocery':ProblityPurchase/Family_size,'Random':1}

	
	Dist = []
	for group in AgeGroups:
		Dist.append(EmploymentDist[group])

	sector_prop 	= np.array(list(map(lambda x,y: np.multiply(x,y),Dist,AgeDist)))
	
	proportions.update(dict(zip(sectors,np.sum(sector_prop,axis=0))))
	
	if sector == None:
		return proportions
	else:
		return proportions[sector]
		
# Applicable for City/Region Wise
def sectors_suspectible(pm1,sector=None,RegionName=None,):
	'''
	returns the proportion of people suspectible in each sector when the entire population is working in that sector
	i.e suspectible population when exactly 1 person works in that sector 
	eg
	P=100  	: people working in sector X
	susp=0.2: returned by this function for sector X
	then for each person in sector X suspected population is P x susp = 20  
	For home, Unemployed, the value is fixed at family size as it is not dependent on total population
	For random it is equal to 4*pi*D*(P/4*pi*D)^cr, where D is density, P is the area population and cr is the compliance Rate ranging between 0 and 1
	'''
	if RegionName == None:
		# For entire City
		sectors 		= pm1.sectors.copy()
		Workplace_Params= pm1.Workplace_Params.copy()
		Family_size 	= pm1.Family_size.copy()[0]
		Total_Pop 		= pm1.Population
		AvgDensity		= pm1.Density # km2 to m2
		# raise


	CR0					= pm1.ComplianceRate
	TN_use_probablity 	= pm1.Prob_use_TN
	Total_Num_Routes 	= pm1.NumRoutes
	Total_Buses			= pm1.NumBuses

	suspectibles 		= {'Home':Family_size}

	for sector in sectors:
		Numbers				 = Workplace_Params[sector]["T"]
		Sizes 			 	 = Workplace_Params[sector]["E"]
		weights 		 	 = np.multiply(Numbers,Sizes)/np.sum(np.multiply(Numbers,Sizes))
		SuspPerSubclass 	 = np.divide(weights,Numbers)
		suspectibles[sector] = np.average(SuspPerSubclass,weights=weights)
		
	#TODO : Check Math later
	Avg_Pop		 				= Total_Pop
 
	suspectibles['Grocery'] 	= (suspectibles['Commerce']+1.0/(Family_size*sum(Workplace_Params["Commerce"]["T"]))) if pm1.CommON else 0
	suspectibles['Unemployed'] 	= sector_proportions(pm1,sector='Unemployed')*Family_size #UPDATE LATER
	suspectibles['Transport'] 	= 0 if Total_Buses ==0 else TN_use_probablity/Total_Buses
	
	Const 						= 4*math.pi*AvgDensity
	suspectibles['Random'] 		= Const*((Avg_Pop/Const)**(1-CR0))
	return suspectibles
		
	
def R0(pm1,c=1,RegionName=None):
	'''
	returns R0 value of the given city
	R0perday = Sum_i P(pop_i) x effective_contact_rate x Suspected_i
	where i is the Place of transmission,
	P(pop_i)  	: Proportion of people experiancing i
	Suspected_i	: Suspected people at i
	R0 		= R0perday x ExpectedIncubationPeriod
	'''
	sectors 		= pm1.sectors.copy()
	Virus_Params 	= pm1.Virus_Params.copy()
	Population 		= pm1.Population
	Workplace_Params= pm1.Workplace_Params.copy()
	Incubation_Per  = pm1.Virus_IncubationPeriod 
	AgeDist 		= pm1.Population_Dist
	suspectibles 	= sectors_suspectible(pm1=pm1)
	proportions 	= sector_proportions(pm1=pm1)

	for sector in sectors:
		Param 	= Workplace_Params[sector]["V"]
		# Weights = np.multiply(Workplace_Params[sector+"_NumberOfSizei"],Workplace_Params[sector+"_ExpectedPeopleInSizei"])
		# avg  	= np.average(Param,axis=0)
		Virus_Params[sector]={'Time':Param[0],'Distance':Param[1]}

	sectors += ['Home','Transport','Grocery','Unemployed','Random']
	Rperday 		= 0
	Rsector = {}
	printdata = []
	for sector in sectors:
		ecr = effective_contact_rate(Virus_Params[sector]['Time'],Virus_Params[sector]['Distance'],c,pm1)
		pop =(proportions[sector])
		if sector in ['Home','Unemployed','Random']:
			susp=(suspectibles[sector])
		else:
			susp=(suspectibles[sector]*Population*pop)
			
		Rsector[sector] = ecr*pop*susp
		
		Rperday += Rsector[sector] 
		printdata.append([sector+":",np.round(ecr,decimals=2),np.round(pop,decimals=2),np.round(susp,decimals=2),np.round(Rsector[sector],decimals=2)])

	EDays 	= np.average(Incubation_Per,weights=AgeDist)
	R0 		= Rperday*EDays
	print("Calib",Workplace_Params)
	print(tabulate(printdata,headers=["Sector","EffContRate","Population","Suspectibles","Rate of sector"]))
	return R0

def calibrate(pm1,R0_val=None):
	if R0_val==None:
		R0_val 	= pm1.Virus_R0 
	Current_R0 	= R0(pm1=pm1)
	c  			= R0_val/Current_R0
	return c
