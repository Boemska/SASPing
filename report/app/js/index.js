//colors from style.scss
var mainCol = '#7ab648';
var gaugeCol = '#ddd';

var timeFormat = d3.time.format("%d/%m/%Y, %H:%M");
var period = 'day';
var worker;

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
  console.log(data);
  if(data.uptime !== null) {
    setGauge(document.querySelector('#uptime .gauge'), data.uptime * 100);
  }
  if(data.avgResponse !== null) {
    document.querySelector('#avg-response-time').innerHTML = data.avgResponse + 'ms';
  }
  if(data.avgLogin !== null) {
    document.querySelector('#avg-login-time').innerHTML = data.avgLogin + 'ms';
  }
  if(data.iqr !== null) {
    document.querySelector('#iqr-time').innerHTML = data.iqr + 'ms';
  }

  drawChart(data.chartData);
}

function drawChart(chartData) {
  //nvd3 chart
  nv.addGraph(function() {
    var chart = nv.models.stackedAreaChart()
      .duration(60)
      .x(function(d) { return d[0]; })
      .y(function(d) { return d[1]; })
      .useInteractiveGuideline(true)
      .showControls(true)
      .clipEdge(true);

    if(chartData.login.length > 0 && chartData.call.length > 0) {
      var firstRequestTime = chartData.login[0][0];

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
          return d3.format(',.1f')(v) + 'ms';
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
