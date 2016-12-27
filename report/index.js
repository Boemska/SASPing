//colors from style.scss
var fontCol = '#91959e';
var mainCol = '#faad39';

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

  var curData = (typeof data !=='undefined' ? data : testData).filter(function(el) {
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
    return req[1] === 'fail' && req[2] !== null;
  }).length || '-';
  document.querySelector('#req-errors').innerHTML = curData.filter(function(req) {
    return req[1] === 'fail' && req[2] === null;
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
      var reason = req[2] === null ? 'Request error' : 'Validation error';
      var issue = req[2] === null ? req[4] : req[2] + ' -> ' + req[3];
      var row = document.createElement('tr');
      var col = document.createElement('td');
      col.innerHTML = reason;
      row.appendChild(col);

      col = document.createElement('td');
      var p = document.createElement('p');
      p.appendChild(document.createTextNode(issue));
      col.appendChild(p);
      row.appendChild(col);

      errorsTableBody.appendChild(row);
    });
  } else {
    errorsTableGridRow.style.display = 'none';
  }

}

document.addEventListener("DOMContentLoaded", function() {
  updateData();
});

// test data
var testData = [
  [1, "fail", "cantContain", "<title>(Stored Process Error|SASStoredProcess)</title>[\\s\\S]*<h2>.*not a valid stored process path.</h2>", null, 1481759319.424848, "1.991 seconds", 1],
  ["test 2", "fail", "mustContain", "\"usermessage\" : \"blank\"", null, 1482450821.47054, "0.055 seconds", 0],
  ["bad url test", "fail", null, null, "No connection adapters were found for 'htt://bad.com'", 1482450821.47054, "0.002 seconds", 0],
  ["successful request", "success", null, null, null, 1482759704.265322, "0.706 seconds", 0]
];
