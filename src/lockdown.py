class lockdown():
    def __init__(self,pm):
        self.SectorLockStatus = dict(zip(pm.transmissionModes,[0]*len(pm.transmissionModes)))
        # for sector in pm.sectors:
        #     self.SectorLockStatus[sector]=0
        self.LockdownLog = []
    def impose_lockdown(self,Today,endday):
        for sector in self.SectorLockStatus:
            if sector not in ['Home','Grocery']:
                self.SectorLockStatus[sector]=1
        self.LockdownLog.append([Today,endday])
    
    def lift_lockdown(self):
        for sector in self.SectorLockStatus:
            self.SectorLockStatus[sector]=0