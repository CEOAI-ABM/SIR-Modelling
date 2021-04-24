class lockdown():
    def __init__(self,pm) -> None:
        self.SectorLockStatus = dict(zip(pm.transmissionModes,[1]*len(pm.transmissionModes)))
        for sector in pm.sectors:
            self.SectorLockStatus[sector]=0
