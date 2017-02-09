/* eslint-env node, browser */
/* globals d3, nv */
//colors from style.scss
var mainCol = '#7ab648';
var gaugeCol = '#ddd';

var appRow = require('./appRow.js');

window.worker.onmessage = function(evt) {
  switch(evt.data.action) {
    case 'error':
      alert(evt.data.msg);
      break;
    case 'update':
      updateData(evt.data.data);
      break;
  }
};

document.addEventListener('DOMContentLoaded', function() {
  window.worker.postMessage({action: 'domReady'});

  var btns = document.querySelectorAll('#time-btns > h3');
  for(var i = 0; i < btns.length; i++) {
    (function(ind) {
      btns[ind].addEventListener('click', function() {
        setPeriod(btns[ind], btns[ind].dataset.period);
      });
    })(i);
  }

  updateMotd();
});

//dom onclick event handler
function setPeriod(el, period) {
  if(el) {
    var btns = document.querySelectorAll('#time-btns > h3');
    for(var i = 0; i < btns.length; i++) {
      btns[i].classList.remove('active');
    }
    el.classList.add('active');
  }

  window.worker.postMessage({
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

  var appTable = document.querySelector('#app-table');
  var domRows = document.querySelectorAll('#app-table .row');
  for(var i = 0; i < domRows.length; i++) {
    appTable.removeChild(domRows[i]);
  }
  for(var key in data.apps) {
    var app = data.apps[key];
    appRow(app.health, key, app.data, app.dataGroupedByExec);
  }
}

function drawChart(chartData) {
  //nvd3 chart
  nv.addGraph(function() {
    var chart = nv.models.stackedAreaChart()
      .duration(60)
      .x(function(d) { return d[0]; })
      // d[2] - true if failed
      .y(function(d) { return !d[2] && d[1] || null; })
      .showControls(false)
      .clipEdge(true)
      .showYAxis(false)
      .style('stream-center')
      .margin({left: 25, right: 25});

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
  if(el.dataset['gaugeInterval']) {
    clearInterval(el.dataset['gaugeInterval']);
  }
  var interval = setInterval(function() {
    try {
      if(percent !== null) {
        el.querySelector('.prec').innerHTML = i + '%';
        var deg = i * 360 / 100;
        el.style['background-image'] = 'linear-gradient('+ (deg <= 180 ? deg+90 : deg-90) +'deg, transparent 50%, '+(deg <= 180 ? gaugeCol : mainCol)+' 50%),linear-gradient(90deg, '+gaugeCol+' 50%, transparent 50%)';
        if(i++ >= percent) {
          clearInterval(interval);
          el.dataset['gaugeInterval'] = interval;
        }
      } else {
        clearInterval(interval);
        el.dataset['gaugeInterval'] = interval;
        el.querySelector('.prec').innerHTML = '-';
        el.style['background-image'] = 'linear-gradient(90deg, transparent 50%, '+gaugeCol+' 50%),linear-gradient(90deg, '+gaugeCol+' 50%, transparent 50%)';
      }
    } catch(e) {
      clearInterval(interval);
      throw e;
    }
  }, 10);
  el.dataset['gaugeInterval'] = interval;
}

function updateMotd() {
  d3.xhr('motd.txt', function(response) {
    if(response.status !== 200) {
      alert('Error loading motd.txt with status code ' + (response.status || 'unknown'));
    } else {
      var motdArr = response.responseText.split('\n');
      if(motdArr[motdArr.length-1] === '') motdArr.pop();
      var motd = motdArr[Math.floor(Math.random() * motdArr.length)];
      document.querySelector('#motd p').innerHTML = motd;
    }
  });
}
