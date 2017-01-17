var Papa = require('papaparse');
var iqr = require('compute-iqr');
self.data = {
  day: {
    uptime: null,
    avgResponse: null,
    avgLogin: null,
    iqr: null,
    apps: {},
    chartData: {
      login: [],
      call: []
    }
  },
  week: {
    uptime: null,
    avgResponse: null,
    avgLogin: null,
    iqr: null,
    apps: {},
    chartData: {
      login: [],
      call: []
    }
  },
  month: {
    uptime: null,
    avgResponse: null,
    avgLogin: null,
    iqr: null,
    apps: {},
    chartData: {
      login: [],
      call: []
    }
  },
  all: {
    uptime: null,
    avgResponse: null,
    avgLogin: null,
    iqr: null,
    apps: {},
    chartData: {
      login: [],
      call: []
    }
  }
};
var dataReady = false;
var pendingSend = false;
var initialDataSent = false;

Papa.parse('../sasping_data.csv', {
  download: true,
  error: function(err) {
    var errMsg = typeof err === 'string' ? err : (err.message || 'no message');
    postMessage({
      action: 'error',
      msg: 'Error loading CSV file with message: ' + errMsg
    });
  },
  complete: function(papaParsedObj) {
    processData(papaParsedObj.data);
  }
});

onmessage = function(evt) {
  switch(evt.data.action) {
    case 'domReady':
      // no break - we want it to go to the next case
    case 'getData':
      //not sending the message if there are requests in queue
      if(dataReady) {
        postMessage({
          action: 'update',
          data: self.data[evt.data.period || 'day']
        });
      } else {
        pendingSend = true;
      }
      break;
  }
};

function processData(data) {
  data.shift(); //remove headings

  var now = new Date();

  var timestamps = {
    day: new Date().setDate(now.getDate() - 1),
    week: new Date().setDate(now.getDate() - 7),
    month: new Date().setMonth(now.getMonth() - 1),
    all: 0
  };


  var count = {
    total: {
      day: 0,
      week: 0,
      month: 0,
      all: 0
    },
    failed: {
      day: 0,
      week: 0,
      month: 0,
      all: 0
    },
    login: {
      day: 0,
      week: 0,
      month: 0,
      all: 0
    },
    call: {
      day: 0,
      week: 0,
      month: 0,
      all: 0
    }
  };
  var time = {
    login: {
      day: 0,
      week: 0,
      month: 0,
      all: 0
    },
    call: {
      day: 0,
      week: 0,
      month: 0,
      all: 0
    }
  };

  var i, period, execTime, execDuration, iqrData;

  for(period in self.data) {
    iqrData = [];
    for(i = 0; i < data.length; i++) {
      if(data[i].length < 9) continue; //empty or not complete row - may be the last one
      if(data[i][5] * 1000 < timestamps[period]) continue; //not in period/timespan

      count.total[period]++;
      if(data[i][1] === 'fail') count.failed[period]++;
      if(data[i][0] === 'sasping login request') {
        count.login[period]++;
        execTime = Math.round(data[i][9] * 1000);
        execDuration = Math.round(parseFloat(data[i][6]) * 1000);
        time.login[period] += execDuration;

        self.data[period].chartData.login.push([
          execTime,
          execDuration,
        ]);
      } else {
        count.call[period]++;
        execDuration = Math.round(parseFloat(data[i][6]) * 1000);
        time.call[period] += execDuration;
        execTime = Math.round(data[i][9] * 1000);

        lastExecCallData = self.data[period].chartData.call[self.data[period].chartData.call.length - 1];
        if(lastExecCallData === undefined || lastExecCallData[0] !== execTime) {
          self.data[period].chartData.call.push([
            execTime,
            [execDuration]
          ]);
        } else {
          lastExecCallData[1].push(execDuration);
        }

        //add to apps
        if(self.data[period].apps[data[i][8]] === undefined) {
          self.data[period].apps[data[i][8]] = [[execTime, execDuration]];
        } else {
          self.data[period].apps[data[i][8]].push([execTime, execDuration]);
        }
      }
      iqrData.push(execDuration);
    }
    for(i = 0; i < self.data[period].chartData.call.length; i++) {
      self.data[period].chartData.call[i][1] = avg(self.data[period].chartData.call[i][1]);
    }
    self.data[period].iqr = iqr(iqrData);

    if(count.total[period] !== 0) {
      self.data[period].uptime = (count.total[period] - count.failed[period]) / count.total[period];
      if(count.call[period]) {
        self.data[period].avgResponse = Math.round(time.call[period] / count.call[period]);
      }
      if(count.login[period]) {
        self.data[period].avgLogin = Math.round(time.login[period] / count.login[period]);
      }
    }

    if(!initialDataSent && pendingSend && period === 'day') {
      postMessage({
        action: 'update',
        data: self.data.day
      });
      initialDataSent = true;
    }
  }
  dataReady = true;
}

function avg(arr) {
  var sum = 0;
  for(var i = 0; i < arr.length; i++) {
    sum += arr[i];
  }
  return sum / arr.length;
}
