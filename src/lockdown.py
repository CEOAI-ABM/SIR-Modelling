class lockdown():
    def __init__(self,pm) -> None:
        self.SectorLockStatus = dict(zip(pm.transmissionModes,[0]*len(pm.transmissionModes)))