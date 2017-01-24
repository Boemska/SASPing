module.exports = function(ledColor, appName, data) {
/*
  <div class="row app-row card">
    <div class="row-content align-children">
      <div>
        <div class="led center-table led-red"></div>
      </div>
      <div>
        <p>Stored process</p>
      </div>
      <div>
        <svg></svg>
      </div>
    </div>
  </div>
*/
  var row = d3.select('#app-table')
      .append('div').attr('class', 'row app-row card')
        .append('div').attr('class', 'row-content align-children');
  row.append('div')
        .append('div').attr('class', 'led center-table led-' + ledColor);
  row.append('div')
        .append('p').text(appName);

  var svgWrapper = row.append('div');
  var svg = svgWrapper.append('svg').style('height', '100px');
  var svgWrapperRect = svgWrapper.node().getBoundingClientRect();

  nv.addGraph({
    generate: function() {
      var chart = nv.models.sparklinePlus()
        .showLastValue(false)
        .width(svgWrapperRect.width)
        .height(svgWrapperRect.height)
        .x(function(d, i) { return i; })
        .y(function(d) { return d[1]; })
        .xTickFormat(function(d) {
          return d3.time.format('%d-%m-%y %H:%M')(new Date(data[d][0]));
        })
        .yTickFormat(function(d) {
          return d / 1000 + ' s';
        })
        .color(function(d) {
          return ledColor;
        });
      svg.datum(data).call(chart);

      nv.utils.windowResize(function() {
        // setTimeout(function() {
          svgWrapperRect = svgWrapper.node().getBoundingClientRect();
          chart.width(svgWrapperRect.width).height(svgWrapperRect.height);
          chart.update();
        // }, 30);
      });
      return chart;
    }
  });
};
