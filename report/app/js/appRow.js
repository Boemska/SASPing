module.exports = function(ledColor, appName, data) {
/*
  <div class="flex-nogrow">
    <div class="led led-red center-table"></div>
  </div>
  <div class="flex-nogrow">
    <p>{{appName}}</p>
  </div>
  <div>
    <svg></svg>
  </div>
*/
  var row = d3.select('#app-table')
      .append('div').style('height', '100px').attr('class', 'row app-row card')
        .append('div').attr('class', 'row-content align-children');
  row.append('div').attr('class', 'flex-nogrow')
        .append('div').attr('class', 'led led-red center-table');
  row.append('div').attr('class', 'flex-nogrow')
        .append('p').text(appName);

  var svg = row.append('div').append('svg');
  var rowBRect = row.node().getBoundingClientRect();

  nv.addGraph({
    generate: function() {
      var chart = nv.models.sparklinePlus()
        .width(rowBRect.width)
        .height(rowBRect.height);
      svg.datum(sine()).call(chart);
      return chart;
    }
  });

  function sine() {
    var sin = [];
    for (var i = 0; i < 100; i++) {
      sin.push({x: i, y: Math.sin(i/10)});
    }
    return sin;
  }
};
