//colors from style.scss
var mainCol = '#7ab648';
var gaugeCol = '#ddd';

var timeFormat = d3.time.format("%d/%m/%Y, %H:%M");

document.addEventListener("DOMContentLoaded", function() {
  updateData();
});

function updateData(el, period) {
  var timePeriodDates = setTimePeriod(el, period);

  Papa.parse('sasping_data.csv', {
    download: true,
    error: function(err) {
      var errMsg = typeof err === 'string' ? err : (err.message || 'no message');
      alert('Error loading csv data with message: ' + errMsg);
    },
    complete: function(papaParsedObj) {
      var data = papaParsedObj.data;
      data.shift(); //remove headings

      var curData = data.filter(function(el) {
        return el[5] > timePeriodDates.prev.getTime()/1000 && el[5] < timePeriodDates.cur.getTime()/1000;
      });

      var avgFn = function(prev, cur, ind, arr) {
        return prev + cur/arr.length;
      };
      var execTimeFn = function(req) {
        return Number(req[6].replace(' seconds', ''));
      };

      var loginReqs = curData.filter(function(req) {
        return req[7] === '1'; //had to login = true
      });
      var wloginReqs = curData.filter(function(req) {
        return req[7] === '0'; //had to login = false
      });

      document.querySelector('#avg-response-time').innerHTML = curData.length === 0 ? '-' : Math.round(curData.map(execTimeFn).reduce(avgFn, 0).toFixed(2) * 1000) + 'ms';
      document.querySelector('#avg-login-time').innerHTML = loginReqs.length === 0 ? '-' : Math.round(loginReqs.map(execTimeFn).reduce(avgFn, 0).toFixed(2) * 1000) + 'ms';
      // document.querySelector('#avg-ping-time').innerHTML = wloginReqs.length === 0 ? '-' : Math.round(wloginReqs.map(execTimeFn).reduce(avgFn, 0).toFixed(2) * 1000) + 'ms';

      drawChart(curData, {login: loginReqs, wlogin: wloginReqs});
    }
  });
}

function setTimePeriod(el, period) {
  var periodEl = document.querySelector('#time-period');
  var cur, prev;

  switch(period) {
    case 'week':
      cur = new Date();
      prev = new Date();
      prev.setDate(cur.getDate() - 7);
      break;
    case 'month':
      cur = new Date();
      prev = new Date();
      prev.setMonth(cur.getMonth() - 1);
      break;
    case 'all':
      cur = new Date();
      prev = new Date();
      prev.setYear(cur.getYear() - 100);
      break;
    default:
      //day
      cur = new Date();
      prev = new Date();
      prev.setDate(cur.getDate() - 1);
  }
  periodEl.innerHTML = timeFormat(prev) + ' - ' + timeFormat(cur);

  if(el) {
    document.querySelectorAll('.time-btn').forEach(function(btn) {
      btn.classList.remove('active');
    });
    el.classList.add('active');
  }

  return {cur: cur, prev: prev};
}

function drawChart(data, requests) {
  //nvd3 chart
  nv.addGraph(function() {
    var chart = nv.models.multiBarChart()
      .duration(60) //transition duration after chart changes
      .reduceXTicks(true)   //If 'false', every single x-axis tick label will be rendered.
      .rotateLabels(0)      //Angle to rotate x-axis labels.
      .showControls(false)   //Allow user to switch between 'Grouped' and 'Stacked' mode.
      .groupSpacing(0.1)    //Distance between each group of bars.
    ;

    chart.xAxis
      .tickFormat(function(d) {
        if(data[data.length - 1][5] - data[0][5] < 24 * 60 * 60) {
          return d3.time.format('%H:%M')(new Date(d));
        } else {
          return d3.time.format('%d-%m-%y')(new Date(d));
        }
      })
      ;

    chart.yAxis
        .tickFormat(function(v) {
          return d3.format(',.1f')(v) + 's';
        });

    chartDataTransformFn = function(req) {
      return {
        x: new Date(req[5] * 1000),
        y: Number(req[6].replace(' seconds', ''))
      };
    };

    d3.select('#main-chart svg')
        .datum([
          {
            key: 'Requests with login',
            values: requests.login.map(chartDataTransformFn)
          }, {
            key: 'Requests without login',
            values: requests.wlogin.map(chartDataTransformFn)
          }
        ])
        .call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
  });
}

function setGauge(el, percent) {
  var i = 0;
  var interval = setInterval(function() {
    try {
      el.querySelector('.prec').innerHTML = i + '%';

      var deg = i * 360 / 100;
      el.style['background-image'] = 'linear-gradient('+ (deg <= 180 ? deg+90 : deg-90) +'deg, transparent 50%, '+(deg <= 180 ? gaugeCol : mainCol)+' 50%),linear-gradient(90deg, '+gaugeCol+' 50%, transparent 50%)';

      if(i++ >= percent) {
        clearInterval(interval);
      }
    } catch(e) {
      clearInterval(interval);
      throw e;
    }
  }, 10);
}
