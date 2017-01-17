module.exports = function(ledColor, appName, data) {
/*
  <div class="row app-row card" style="height: 100px;">
    <div class="row-content align-children">
      <div class="flex-nogrow">
        <div class="led led-red center-table"></div>
      </div>
      <div class="flex-nogrow">
        <p>Stored process</p>
      </div>
      <div>
        <svg></svg>
      </div>
    </div>
  </div>
*/
  var row = d3.select('#app-table')
      .append('div').style('height', '100px').attr('class', 'row app-row card')
        .append('div').attr('class', 'row-content align-children');
  row.append('div').attr('class', 'flex-nogrow')
        .append('div').attr('class', 'led center-table led-' + ledColor);
  row.append('div').attr('class', 'flex-nogrow')
        .append('p').text(appName);

  var svgWrapper = row.append('div');
  var svg = svgWrapper.append('svg');
  var svgWrapperRect = svgWrapper.node().getBoundingClientRect();

  nv.addGraph({
    generate: function() {
      var chart = nv.models.sparklinePlus()
        .width(svgWrapperRect.width)
        .height(svgWrapperRect.height)
        .x(function(d, i) { return i; })
        .y(function(d) { return d[1]; })
        .xTickFormat(function(d) {
          return d3.time.format('%d-%m-%y %H:%M')(new Date(data[d][0]));
        })
        .yTickFormat(function(d) {
          return d + ' ms';
        })
        .color(function(d) {
          return ledColor;
        });
      svg.datum(data).call(chart);
      return chart;
    }
  });
};
