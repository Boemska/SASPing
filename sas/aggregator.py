import calendar
import datetime
import time
import copy
import csv
import json
import os

from .response import Response

class Aggregator:
    def __init__(self, inFile, max, descDataFilePath):
        self._inFile = inFile
        self._descDataFilePath = descDataFilePath
        self._max = max
        self._data = [
            [], # all time
            [], # month
            [], # week
            [] # day
        ]
        self._shouldRead = True


        if os.path.isfile(self._descDataFilePath):
            with open(self._descDataFilePath, 'r') as file:
                self._descData = json.load(file)
        else:
            self._descData = {}

        if not(self._descData.has_key('month_file_pos')):
            self._descData['month_file_pos'] = 0
        if not(self._descData.has_key('week_file_pos')):
            self._descData['week_file_pos'] = 0
        if not(self._descData.has_key('day_file_pos')):
            self._descData['day_file_pos'] = 0

        self._descData['last_run'] = int(time.time())
        self.saveDescData()

    def saveDescData(self):
        with open(self._descDataFilePath, 'w') as file:
            file.write(json.dumps(self._descData))

    def readWholeFile(self):
        self._inFile.seek(0)
        self._read()

    def readFilePart(self, fromBlock):
        self._inFile.seek(fromBlock)
        self._read()

    def _read(self):
        self._inFile.readline() #skip headers if we are starting from beginning
        fieldNames = Response.getKeys()
        reader = csv.DictReader(self._inFile, fieldnames=fieldNames)
        timestamps = [
            0,
            Aggregator.getMonthOldTimestamp(),
            Aggregator.getWeekOldTimestamp(),
            Aggregator.getDayOldTimestamp(),
        ]
        testsInRun = []

        # for the position in file, that should be updated every time the whole file is read
        positionUpdated = [[True, 'all'], [False, 'month'], [False, 'week'], [False, 'day']]

        lastBlock = self._inFile.tell()
        blockSize = 0

        for row in reader:
            # find the biggest block size to start from the currentBlock - blockSize when reading just a part
            if blockSize < self._inFile.tell() - lastBlock:
                blockSize = self._inFile.tell() - lastBlock
            lastBlock = self._inFile.tell()

            # remove unused data
            del row['failed test group']
            del row['failed pattern']
            del row['message']

            try:
                row['timestamp'] = int(row['timestamp'])
                row['program exec timestamp'] = int(row['program exec timestamp'])
            except:
                print("Ignoring row:\n'{0}'".format(row))
                print("Reason: corrupted integer values")
                continue

            if row['id'] == 'sasping login request':
                if len(testsInRun) > 0: # check only for the first exec
                    timestamp = testsInRun[0]['program exec timestamp']
                    for i in range(len(timestamps)):
                        if timestamp > timestamps[i]:
                            self._data[i].append(testsInRun)
                            # save position of the data older than month, week, day
                            # we are using this to read only part of the file with recent data
                            if not(positionUpdated[i][0]):
                                positionUpdated[i][0] = True
                                self._descData[positionUpdated[i][1] + '_file_pos'] = self._inFile.tell() - blockSize
                testsInRun = [row]
            else:
                testsInRun.append(row)
        # add last row
        for i in range(len(timestamps)):
            self._data[i].append(testsInRun)

        self._shouldRead = False
        self.saveDescData()

    def shouldUpdateAll(self):
        try:
            if int(time.time()) - self._descData['all_time_updated'] > self._descData['all_time_interval']:
                return True
        except KeyError:
            return True
        return False

    def shouldUpdateMonth(self):
        try:
            if int(time.time()) - self._descData['month_time_updated'] > self._descData['month_time_interval']:
                return True
        except KeyError:
            return True
        return False

    def shouldUpdateWeek(self):
        try:
            if int(time.time()) - self._descData['week_time_updated'] > self._descData['week_time_interval']:
                return True
        except KeyError:
            return True
        return False

    def getLatestUpdateTime(self):
        return self._descData['latest_time_updated'] if self._descData.has_key('latest_time_updated') else 0

    def getShrinkedAllTimeData(self):
        if self._shouldRead:
            self.readWholeFile()
        aggreagatedData = Aggregator.shrink(self._data[0], self._max)
        if len(aggreagatedData) >= 2:
            # use average time
            self._descData['all_time_interval'] = (aggreagatedData[-1][0]['program exec timestamp'] - aggreagatedData[0][0]['program exec timestamp']) / len(aggreagatedData)
        else:
            self._descData['all_time_interval'] = 0
        self._descData['all_time_updated'] = int(time.time())
        self.saveDescData()
        return aggreagatedData

    def getShrinkedMonthData(self):
        if self._shouldRead:
            self.readFilePart(self._descData['month_file_pos'])
        aggreagatedData = self.shrink(self._data[1], self._max)
        if len(aggreagatedData) >= 2:
            # use average time
            self._descData['month_time_interval'] = (aggreagatedData[-1][0]['program exec timestamp'] - aggreagatedData[0][0]['program exec timestamp']) / len(aggreagatedData)
        else:
            self._descData['month_time_interval'] = 0
        self._descData['month_time_updated'] = int(time.time())
        self.saveDescData()
        return aggreagatedData

    def getShrinkedWeekData(self):
        if self._shouldRead:
            self.readFilePart(self._descData['week_file_pos'])
        aggreagatedData = self.shrink(self._data[2], self._max)
        if len(aggreagatedData) >= 2:
            self._descData['week_time_interval'] = (aggreagatedData[-1][0]['program exec timestamp'] - aggreagatedData[0][0]['program exec timestamp']) / len(aggreagatedData)
        else:
            self._descData['week_time_interval'] = 0
        self._descData['week_time_updated'] = int(time.time())
        self.saveDescData()
        return aggreagatedData

    def getDayData(self):
        if self._shouldRead:
            self.readFilePart(self._descData['day_file_pos'])
        self._descData['latest_time_updated'] = int(time.time())
        self.saveDescData()
        return self._data[3]

    @staticmethod
    def shrink(col, max):
        if len(col) < max:
            return col
        newCol = []
        colSize = len(col)
        if colSize == 0:
            return newCol
        maxTestsInRun = reduce(lambda x, y: x if x > len(y) else len(y), col, 0)
        divider = 2

        while colSize/divider > max:
            divider += 2

        newColSize = colSize / divider

        for i in range(newColSize):
            run = []
            for k in range(maxTestsInRun):
                try:
                    row = None
                    status = 1
                    programExecTimestamps = []
                    execTimestamps = []
                    execDurations = []
                    statuses = []
                    for j in range(divider):
                        # we can use this value from any row in the same collector run
                        programExecTimestamps.append(col[i*divider+j][0]['program exec timestamp'])
                        # check if k index is not out of bounds
                        # some executions have more tests than others
                        if len(col[i*divider+j]) > k:
                            execTimestamps.append(col[i*divider+j][k]['timestamp'])
                            execDurations.append(float(col[i*divider+j][k]['execution duration (s)']))
                            statuses.append(col[i*divider+j][k]['status'])
                            if row == None:
                                # use any of defined rows for other properties like id, had to login, etc.
                                row = copy.copy(col[i*divider+j][k])
                    if row != None:
                        row['status'] = '1' if statuses.count('1') >= len(statuses)/2 else None
                        row['program exec timestamp'] = Aggregator.avg(programExecTimestamps)
                        row['timestamp'] = Aggregator.avg(execTimestamps)
                        row['execution duration (s)'] = round(Aggregator.avg(execDurations), 3)
                        run.append(row)
                except Exception as e:
                    # ignore row if data is corrupted
                    print("Ignoring row in shrink\n'{0}'".format(row))
                    print("Ignoring row:\n'{0}'".format(row))
                    print("Reason: exception thrown in shrink with error: {0}".format(str(e)))
                    continue
            newCol.append(run)
        return newCol

    @staticmethod
    def avg(list):
        return sum(list) / len(list)

    @staticmethod
    def getMonthOldTimestamp():
        today = datetime.datetime.today()
        monthDays = calendar.monthrange(today.year, today.month)[1]
        return Aggregator._getDaysOldTimestamp(monthDays)

    @staticmethod
    def getWeekOldTimestamp():
        return Aggregator._getDaysOldTimestamp(7)

    @staticmethod
    def getDayOldTimestamp():
        return Aggregator._getDaysOldTimestamp(1)

    @staticmethod
    def _getDaysOldTimestamp(days):
        today = datetime.datetime.today()
        return int(time.mktime((datetime.date.today() - datetime.timedelta(days)).timetuple()))
