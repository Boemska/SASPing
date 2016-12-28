//colors from style.scss
var fontCol = '#91959e';
var mainCol = '#faad39';
var backCol = '#2f2f2f';

function setGauge(el, percent) {
  var i = 0;
  var interval = setInterval(function() {
    try {
      el.querySelector('.prec').innerHTML = i + '%';

      var deg = i * 360 / 100;
      el.style['background-image'] = 'linear-gradient('+ (deg <= 180 ? deg+90 : deg-90) +'deg, transparent 50%, '+(deg <= 180 ? fontCol : mainCol)+' 50%),linear-gradient(90deg, '+fontCol+' 50%, transparent 50%)';

      if(i++ >= percent) {
        clearInterval(interval);
      }
    } catch(e) {
      clearInterval(interval);
      throw e;
    }
  }, 10);
}

function updateData(el, period) {
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
  // TODO: change prev to first timestamp if smaller
  periodEl.innerHTML = prev.toLocaleString(navigator.language) + ' - ' + cur.toLocaleString(navigator.language);

  if(el) {
    document.querySelectorAll('.time-btn').forEach(function(btn) {
      btn.classList.remove('active');
    });
    el.classList.add('active');
  }

  Papa.parse('/sasping_data.csv', {
    download: true,
    complete: function(papaParsedObj) {
      var data = papaParsedObj.data;
      data.shift(); //remove headings

      var curData = data.filter(function(el) {
        return el[5] > prev.getTime()/1000 && el[5] < cur.getTime()/1000;
      });

      var avgFn = function(prev, cur, ind, arr) {
        return prev + cur/arr.length;
      };
      var execTimeFn = function(req) {
        return Number(req[6].replace(' seconds', ''));
      };

      var successfulReqs = curData.filter(function(req) {
        return req[1] === 'success';
      }).length;
      var loginReqs = curData.filter(function(req) {
        return req[7] === 1; //had to login = true
      });
      var wloginReqs = curData.filter(function(req) {
        return req[7] === 0; //had to login = false
      });

      document.querySelector('#total-reqs').innerHTML = curData.length;
      setGauge(document.querySelector('#succ-req .gauge'),successfulReqs === 0 ? 0 : Math.round((successfulReqs / curData.length).toFixed(2) * 100));
      document.querySelector('#avg-req-time').innerHTML = curData.length === 0 ? '-' : Math.round(curData.map(execTimeFn).reduce(avgFn, 0).toFixed(2) * 100) + 'ms';
      document.querySelector('#avg-login-req-time').innerHTML = loginReqs.length === 0 ? '-' : Math.round(loginReqs.map(execTimeFn).reduce(avgFn, 0).toFixed(2) * 100) + 'ms';
      document.querySelector('#avg-wologin-req-time').innerHTML = wloginReqs.length === 0 ? '-' : Math.round(wloginReqs.map(execTimeFn).reduce(avgFn, 0).toFixed(2) * 100) + 'ms';
      document.querySelector('#validation-errors').innerHTML = curData.filter(function(req) {
        return req[1] === 'fail' && req[2];
      }).length || '-';
      document.querySelector('#req-errors').innerHTML = curData.filter(function(req) {
        return req[1] === 'fail' && !req[2];
      }).length || '-';

      var errorsTableGridRow = document.querySelector('#errors-table-row');
      var errorsTable = document.querySelector('#errors-table-row table');
      var errorsTableBody = document.querySelector('#errors-table-row table tbody');
      errorsTableBody.innerHTML = ''; //remove all rows

      var errorReqs = curData.filter(function(req) {
        return req[1] === 'fail';
      });
      if(errorReqs.length > 0) {
        errorsTableGridRow.style.display = '';
        errorReqs.forEach(function(req) {
          var id = req[0];
          var execTime = new Date(req[5] * 1000);
          var row = document.createElement('tr');
          var col = document.createElement('td');
          col.innerHTML = id;
          row.appendChild(col);

          col = document.createElement('td');
          col.innerHTML = execTime.toLocaleString(navigator.language);
          row.appendChild(col);

          col = document.createElement('td');
          col.classList.add('has-tooltip');
          col.setAttribute('title', !req[2] ? req[4] : req[2] + ' -> ' + req[3]);
          col.innerHTML = !req[2] ?
                            'Stored Process Application failed to respond' :
                            'SAS Stored Process application failed to validate';
          row.appendChild(col);

          errorsTableBody.appendChild(row);
        });
      } else {
        errorsTableGridRow.style.display = 'none';
      }

      Highcharts.chart(document.querySelector('#main-chart > div'), {
        chart: {
            type: 'column',
            height: 200,
            backgroundColor: backCol
        },
        legend: {
          itemStyle: {
            color: fontCol
          }
        },
        title: null,
        xAxis: {
          type: 'datetime',
          dateTimeLabelFormats: {
            minute: '%Y-%m-%d<br/>%H:%M',
                    hour: '%Y-%m-%d<br/>%H:%M',
                    day: '%Y<br/>%m-%d',
                    week: '%Y<br/>%m-%d',
                    month: '%Y-%m',
                    year: '%Y'
          }
        },
        series: [
          {
            name: 'Requests with login',
            data: loginReqs.map(function(req) {
              return {
                x: new Date(req[5] * 1000),
                y: Number(req[6].replace(' seconds', ''))
              };
            })
          }, {
            name: 'Requests without login',
            data: wloginReqs.map(function(req) {
              return {
                x: new Date(req[5] * 1000),
                y: Number(req[6].replace(' seconds', ''))
              };
            })
          }
        ]
      });

      tlite(function(el) {
        return el.classList.contains('has-tooltip') && {grav: 'se'};
      });
    }
  });
}

document.addEventListener("DOMContentLoaded", function() {
  updateData();
});
