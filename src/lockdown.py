class lockdown():
    def __init__(self,pm):
        self.SectorLockStatus = dict(zip(pm.transmissionModes,[0]*len(pm.transmissionModes)))
        # for sector in pm.sectors:
        #     self.SectorLockStatus[sector]=0
        self.LockdownLog = []
