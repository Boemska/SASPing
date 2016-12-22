
class Response:
    def __init__(self, status, failedTestGroup=None, failedPatt=None, message=None):
        self.id              = None
        self.status          = status
        self.failedTestGroup = failedTestGroup
        self.failedPatt      = failedPatt
        self.message         = message
        self.hadToLogin      = False

    def addTime(self, timestamp, execTime):
        self.timestamp = timestamp
        self.execTime  = execTime
        return self

    def setHadToLoginFlag(self):
        self.hadToLogin = True
        return self

    def setId(self, id):
        self.id = id
        return self

    def __iter__(self):
        yield 'id', self.id
        yield 'status', self.status
        yield 'failed test group', self.failedTestGroup
        yield 'failed pattern', self.failedPatt
        yield 'message', self.message
        yield 'timestamp', self.timestamp
        yield 'execution time', self.execTime
        yield 'had to login', 1 if self.hadToLogin else 0
        
