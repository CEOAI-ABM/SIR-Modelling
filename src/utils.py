from .calibration import sector_proportions
def get_Numbers(pm):
	sec_prop = sector_proportions(pm)
	for sector in pm.sectors:
		pop = int(sec_prop[sector]*pm.Population)
		pm.Workplace_Params[sector]["T"] = list(map(lambda x,y: max(int((pop*x)//y),1),pm.Workplace_Params[sector]["N"],pm.Workplace_Params[sector]["E"] ))
	return pm.Workplace_Params