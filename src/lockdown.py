class lockdown():
    def __init__(self,pm):
        self.SectorLockStatus = dict(zip(pm.transmissionModes,[0]*len(pm.transmissionModes)))
        self.LockdownPhases   = pm.LockdownPhases.copy()
        # for sector in pm.sectors:
        #     self.SectorLockStatus[sector]=0
        self.LockdownLog      = []
        self.__PreviousCR__   = 0
        self.InLockdown       = False
        self.__OnGoingLocks__ = []

    def impose_lockdown(self,endday,scrut,aff_sec ):
        for sector in self.SectorLockStatus:
            if (aff_sec=="Complete" and sector not in ['Home','Grocery'])or sector ==aff_sec:
                self.SectorLockStatus[sector] = 1
        self.LockdownLog.append([self.Today,endday]) if aff_sec  == "Complete" else 0
    
    def lift_lockdown(self):
        for sector in self.SectorLockStatus:
            self.SectorLockStatus[sector] = 0
    def unlock_sector(self, Sector):
        self.SectorLockStatus[Sector] = 0

    def __apply_lockdown__(self,lock):
        _,_,_,scrut,sectors,CR,_,period = lock
        end_day = self.Today+period
        if self.InLockdown == True:
            for i, prev_lock in enumerate(self.__OnGoingLocks__):
                if prev_lock[1] == sectors: # find the previous region lock
                    self.__OnGoingLocks__[i][0] = end_day # set the end date of prev lock as the end date of new lock
                    break
        else:
            self.impose_lockdown(end_day,scrut,sectors)
            self.__OnGoingLocks__.append([end_day, sectors])
            

        self.LockdownPhases.remove(lock)
        # self.impose_lockdown(self.Today,self.Today+period,scrut)
        if CR is not None:
            self.__PreviousCR__ = self.ComplianceRate
            self.ComplianceRate = CR
    def __check_ongoing_locks__(self):
        """
        Iterates over the ongoing locks and lifts locks when the time is up.
        The tuples in self.OngoingLocks are like -> (Day lock ends, sector locked)
        """
        tempOngoingLocks = self.__OnGoingLocks__.copy()
        for OGLock in tempOngoingLocks:
            end_day,sectors =  OGLock
            if self.Today == end_day:
                if sectors == "Complete": # Region OGLock
                    self.lift_lockdown()
                    self.ComplianceRate = self.__PreviousCR__
                else: # Sector OGLock
                    self.unlock_sector(sectors)
                self.__OnGoingLocks__.remove(OGLock)
                
    def daily_lockdown(self):
        self.__check_ongoing_locks__()
        temp  = self.LockdownPhases.copy()
        #lock[0] start day
        #lock[1] duration
        #lock[2] type
        #lock[3] Scrutiny
        #lock[4] sectors
        #lock[5] CR
        #lock[6] Threshold
        #lock[7] period
        curr_postive = len(self.TestedP['Positive'])
        for lock in temp:
            start,duration,_,scrut,_,CR,Thresh,_ = lock
            end = start+duration

            if self.Today>end: #If end date has passed remove lock
                self.LockdownPhases.remove(lock)
            elif start<=self.Today and self.Today<=end:
                if scrut == "Hard":
                    self.__apply_lockdown__(lock)
                elif scrut == "TAbsoulte" and curr_postive>=Thresh:
                    self.__apply_lockdown__(lock)
                elif scrut == "TRelative" and curr_postive-self.__prev_positive__>=Thresh:
                    self.__apply_lockdown__(lock)

        self.__prev_positive__ 		= curr_postive
