var iqr = require('compute-iqr');
var Papa = require('papaparse');

self.dataReady = false;
self.pendingSend = false;
self.initialDataSent = false;

function update(callback) {
  Papa.parse('../sasping_data_latest.csv', {
    download: true,
    error: function(err) {
      var errMsg = typeof err === 'string' ? err : (err.message || 'no message');
      postMessage({
        action: 'error',
        msg: 'Error loading CSV file with message: ' + errMsg
      });
    },
    complete: function(papaParsedObj) {
      updateLatest(papaParsedObj.data);
      callback();

      setTimeout(function() {
        updateWeek();
        updateMonth();
        updateAll();
      }, 0);
    }
  });
}

update(function() {
  if(!self.initialDataSent && self.pendingSend) {
    postMessage({
      action: 'update',
      data: self.processedData['day']
    });
    self.initialDataSent = true;
    self.pendingSend = false;
  }
});

setTimeout(update, 10 * 60 * 1000);

onmessage = function(evt) {
  switch(evt.data.action) {
    case 'domReady':
      // no break - we want it to go to the next case
    case 'getData':
      //not sending the message if there are requests in queue
      if(!self.pendingSend && self.processedData[evt.data.period || 'day']) {
        postMessage({
          action: 'update',
          data: self.processedData[evt.data.period || 'day']
        });
        self.pendingSend = false;
      } else {
        self.pendingSend = true;
      }
      break;
  }
};

self.processedData = {
  'day': null,
  'week': null,
  'month': null,
  'all': null
}

function updateLatest(data) {
  var now = new Date();
  var dayOldTimestamp = new Date().setDate(now.getDate() - 1);
  self.processedData['day'] = processData(data, dayOldTimestamp);
}

function updateWeek() {
  Papa.parse('../sasping_data_week.csv', {
    download: true,
    error: function(err) {
      var errMsg = typeof err === 'string' ? err : (err.message || 'no message');
      postMessage({
        action: 'error',
        msg: 'Error loading CSV file with message: ' + errMsg
      });
    },
    complete: function(papaParsedObj) {
      var now = new Date();
      var weekldTimestamp = new Date().setDate(now.getDate() - 7)
      self.processedData['week'] = processData(papaParsedObj.data, weekldTimestamp);
    }
  });
}
function updateMonth() {
  Papa.parse('../sasping_data_month.csv', {
    download: true,
    error: function(err) {
      var errMsg = typeof err === 'string' ? err : (err.message || 'no message');
      postMessage({
        action: 'error',
        msg: 'Error loading CSV file with message: ' + errMsg
      });
    },
    complete: function(papaParsedObj) {
      var now = new Date();
      var monthOldTimestamp = new Date().setMonth(now.getMonth() - 1)
      self.processedData['month'] = processData(papaParsedObj.data, monthOldTimestamp);
    }
  });
}
function updateAll() {
  Papa.parse('../sasping_data_allTime.csv', {
    download: true,
    error: function(err) {
      var errMsg = typeof err === 'string' ? err : (err.message || 'no message');
      postMessage({
        action: 'error',
        msg: 'Error loading CSV file with message: ' + errMsg
      });
    },
    complete: function(papaParsedObj) {
      self.processedData['all'] = processData(papaParsedObj.data, 0);
    }
  });
}

function processData(data, timestamp) {
  if(data[data.length - 1].length === 1) data.pop(); //remove last row if it's empty

  var processedData = {
    uptime: null,
    avgResponse: null,
    avgLogin: null,
    iqr: null,
    apps: {},
    chartData: {
      login: [],
      call: []
    }
  };
  var count = {
    total: 0,
    failed: 0,
    login: 0,
    call: 0
  };
  var time = {
    login: 0,
    call: 0
  };

  var i, execTime, execDuration, iqrData, lastExecCallData;
  var failedCheckFn = function(status) {
    return !status;
  };

  iqrData = [];
  for(i = data.length-1; i >= 0; i--) {
    if(data[i][2] * 1000 < timestamp) break; //not in period/timespan

    count.total++;
    if(!data[i][1]) count.failed++;
    if(data[i][0] === 'sasping login request') {
      count.login++;
      execTime = Number(data[i][6]) * 1000;
      execDuration = data[i][3] * 1000;
      time.login += execDuration;

      processedData.chartData.login.push([
        execTime,
        execDuration,
      ]);
    } else {
      count.call++;
      execDuration = data[i][3] * 1000;
      time.call += execDuration;
      execTime = Number(data[i][6]) * 1000;

      lastExecCallData = processedData.chartData.call[processedData.chartData.call.length - 1];
      if(lastExecCallData === undefined || lastExecCallData[0] !== execTime) {
        processedData.chartData.call.push([
          execTime,
          [execDuration]
        ]);
      } else {
        lastExecCallData[1].push(execDuration);
      }

      //add to apps
      if(processedData.apps[data[i][5]] === undefined) {
        processedData.apps[data[i][5]] = {
          data: [[data[i][2] * 1000, execDuration]]
        };
      } else {
        processedData.apps[data[i][5]].data.push([data[i][2] * 1000, execDuration]);
      }
    }
    iqrData.push(execDuration);
  }

  //set app health status
  for(var appName in processedData.apps) {
    i = data.length - 1;
    var lastExecTime = Number(data[i][6]);
    var lastExecStatuses = [];
    while(lastExecTime === Number(data[i][6])) {
      if(appName === data[i][5]) {
        lastExecStatuses.push(data[i][1]);
      }
      i--;
    }
    if(lastExecStatuses.every(failedCheckFn)) {
      processedData.apps[appName].health = 'red';
    } else if(lastExecStatuses.some(failedCheckFn)) {
      processedData.apps[appName].health = 'orange';
    } else {
      processedData.apps[appName].health = 'green';
    }
  }

  for(i = 0; i < processedData.chartData.call.length; i++) {
    processedData.chartData.call[i][1] = avg(processedData.chartData.call[i][1]);
  }
  processedData.iqr = iqr(iqrData);

  if(count.total !== 0) {
    processedData.uptime = ((count.total - count.failed) / count.total).toFixed(2);
    if(count.call) {
      processedData.avgResponse = Math.round(time.call / count.call);
    }
    if(count.login) {
      processedData.avgLogin = Math.round(time.login / count.login);
    }
  }

  return processedData;
}

function avg(arr) {
  var sum = 0;
  for(var i = 0; i < arr.length; i++) {
    sum += arr[i];
  }
  return sum / arr.length;
}
