
class Response:
    def __init__(self, id, status, failedTestGroup=None, failedPatt=None, message=None, timestamp=None, execTime=None, hadToLogin=False, appName=None, programExecTime=None):
        self.id              = id
        self.status          = status
        self.failedTestGroup = failedTestGroup
        self.failedPatt      = failedPatt
        self.message         = message
        self.timestamp       = timestamp
        self.execTime        = execTime
        self.hadToLogin      = hadToLogin
        self.appName         = appName
        self.programExecTime = programExecTime

    def setTime(self, timestamp, execTime):
        self.timestamp = timestamp
        self.execTime  = execTime
        return self

    def setHadToLoginFlag(self):
        self.hadToLogin = True
        return self

    def setId(self, id):
        self.id = id
        return self

    def setAppName(self, appName):
        self.appName = appName;
        return self

    def setProgramExecTime(self, time):
        self.programExecTime = time;
        return self

    @staticmethod
    def getKeys():
        return [
            'id',
            'status',
            'failed test group',
            'failed pattern',
            'message',
            'timestamp',
            'execution duration (s)',
            'had to login',
            'application name',
            'program exec timestamp'
        ]

    def __iter__(self):
        # for boolean 1 is true, None (empty in csv) is false
        # this is also convenient in JS where empty is falsy value
        yield 'id', self.id
        yield 'status', 1 if self.status == 'success' else None
        yield 'failed test group', self.failedTestGroup
        yield 'failed pattern', self.failedPatt
        yield 'message', self.message
        yield 'timestamp', int(self.timestamp)
        yield 'execution duration (s)', round(self.execTime, 3)
        yield 'had to login', 1 if self.hadToLogin else None
        yield 'application name', self.appName or ''
        yield 'program exec timestamp', int(self.programExecTime)
