//colors from style.scss
var mainCol = '#7ab648';
var gaugeCol = '#ddd';

var timeFormat = d3.time.format("%d/%m/%Y, %H:%M");
var period = 'day';
var worker;

var appRow = require('./appRow.js');

var MyWorker = require('worker-loader!./worker.js');
try {
  worker = new MyWorker();
} catch(e) {
  if(e instanceof ReferenceError) {
    alert('Your browser does not support web workers.');
  }
  throw e;
}

worker.onmessage = function(evt) {
  switch(evt.data.action) {
    case 'error':
      alert(evt.data.msg);
      break;
    case 'update':
      updateData(evt.data.data);
      getDataInterval = null;
      break;
  }
};

document.addEventListener("DOMContentLoaded", function() {
  worker.postMessage({action: 'domReady'});

  document.querySelectorAll('#time-btns > h3').forEach(function(el) {
    el.addEventListener('click', function(evt) {
      setPeriod(el, el.dataset.period);
    });
  });

  updateMotd();
});

//dom onclick event handler
function setPeriod(el, period) {
  period = period;

  if(el) {
    document.querySelectorAll('.time-btn').forEach(function(btn) {
      btn.classList.remove('active');
    });
    el.classList.add('active');
  }

  worker.postMessage({
    action: 'getData',
    period: period
  });
}


function updateData(data) {
  if(data.uptime !== null && !isNaN(data.uptime)) {
    setGauge(document.querySelector('#uptime .gauge'), data.uptime * 100);
  } else {
    setGauge(document.querySelector('#uptime .gauge'), null);
  }
  if(data.avgResponse !== null && !isNaN(data.avgResponse)) {
    document.querySelector('#avg-response-time').innerHTML = data.avgResponse + ' ms';
  } else {
    document.querySelector('#avg-response-time').innerHTML = '-';
  }
  if(data.avgLogin !== null && !isNaN(data.avgLogin)) {
    document.querySelector('#avg-login-time').innerHTML = data.avgLogin + ' ms';
  } else {
    document.querySelector('#avg-login-time').innerHTML = '-';
  }
  if(data.iqr !== null && !isNaN(data.iqr)) {
    document.querySelector('#iqr-time').innerHTML = data.iqr + ' ms';
  } else {
    document.querySelector('#iqr-time').innerHTML = '-';
  }

  drawChart(data.chartData);

  document.querySelector('#app-table').innerHTML = '';
  for(var key in data.apps) {
    appRow(data.apps[key].health, key, data.apps[key].data);
  }
}

function drawChart(chartData) {
  //nvd3 chart
  nv.addGraph(function() {
    var chart = nv.models.stackedAreaChart()
      .duration(60)
      .x(function(d) { return d[0]; })
      .y(function(d) { return d[1]; })
      .showControls(false)
      .clipEdge(true)
      .showYAxis(false)
      .style('stream-center');

    if(chartData.login.length > 0 && chartData.call.length > 0) {
      //the array is reverse - last to first
      var firstRequestTime = chartData.login[chartData.login.length-1][0];

      chart.xAxis.tickFormat(function(d) {
        if(Date.now() - firstRequestTime < 24 * 60 * 60 * 1000) {
          return d3.time.format('%H:%M')(new Date(d));
        } else {
          return d3.time.format('%d-%m-%y')(new Date(d));
        }
      });
    }

    chart.yAxis
        .tickFormat(function(v) {
          return (v/1000).toFixed(3).replace(/00?$/, '') + ' s';
        });

    d3.select('#main-chart svg')
        .datum([{
            key: 'Call requests',
            values: chartData.call
          }, {
            key: 'Login requests',
            values: chartData.login
        }])
        .call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
  });
}

function setGauge(el, percent) {
  var i = 0;
  var interval = setInterval(function() {
    try {
      if(percent !== null) {
        el.querySelector('.prec').innerHTML = i + '%';
        var deg = i * 360 / 100;
        el.style['background-image'] = 'linear-gradient('+ (deg <= 180 ? deg+90 : deg-90) +'deg, transparent 50%, '+(deg <= 180 ? gaugeCol : mainCol)+' 50%),linear-gradient(90deg, '+gaugeCol+' 50%, transparent 50%)';
        if(i++ >= percent) {
          clearInterval(interval);
        }
      } else {
        clearInterval(interval);
        el.querySelector('.prec').innerHTML = '-';
        el.style['background-image'] = 'linear-gradient(90deg, transparent 50%, '+gaugeCol+' 50%),linear-gradient(90deg, '+gaugeCol+' 50%, transparent 50%)';
      }
    } catch(e) {
      clearInterval(interval);
      throw e;
    }
  }, 10);
}

function updateMotd() {
  d3.xhr('motd.txt', function(response) {
    if(response.status !== 200) {
      alert('Error loading motd.txt with status code ' + (err.status || 'unknown'));
    } else {
      var motdArr = response.responseText.split('\n');
      if(motdArr[motdArr.length-1] === '') motdArr.pop();
      var motd = motdArr[Math.floor(Math.random() * motdArr.length)];
      document.querySelector('#motd p').innerHTML = motd;
    }
  });
}
