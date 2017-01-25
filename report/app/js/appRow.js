/* eslint-env node, browser */
/* globals d3, nv */
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

  var svgWrapper = row.append('div').style('height', '100px');
  var svgWrapperRect = svgWrapper.node().getBoundingClientRect();
  var svg = svgWrapper.append('svg')
                      .style('height', '100%')
                      .attr('width', svgWrapperRect.width - 100)
                      .style('margin', '0 50px')
                      .attr('class', 'sparkline');
  var svgRect = svg.node().getBoundingClientRect();

  // nv.addGraph({
  //   generate: function() {
  //     var chart = nv.models.sparklinePlus()
  //       .showLastValue(false)
  //       .width(svgWrapperRect.width)
  //       .height(svgWrapperRect.height)
  //       .x(function(d, i) { return i; })
  //       // line wont break
  //       // .y(function(d) { return d.failed && d.y || null; })
  //       .y(function(d) { return d.y; })
  //       .xTickFormat(function(d) {
  //         return d3.time.format('%d-%m-%y %H:%M')(new Date(data[d].x));
  //       })
  //       .yTickFormat(function(d) {
  //         return d / 1000 + ' s';
  //       })
  //       .color(function() {
  //         return ledColor;
  //       })
  //       .showMinMaxPoints(false);
  //     svg.datum(data).call(chart);
  //
  //     nv.utils.windowResize(function() {
  //       svgWrapperRect = svgWrapper.node().getBoundingClientRect();
  //       chart.width(svgWrapperRect.width).height(svgWrapperRect.height);
  //       chart.update();
  //     });
  //     return chart;
  //   }
  // });

  var margin = {top: 20, right: 80, bottom: 30, left: 250};
  // Parse the date / time
  var timeFormat;

  if(data[0].x - data[data.length-1].x > 24 * 60 * 60 * 1000) {
    timeFormat = d3.time.format('%d-%m-%y');
  } else {
    timeFormat = d3.time.format('%H:%M');
  }


  // Set the ranges
  var x = d3.scale.linear().range([svgRect.width - 10, 0]);
  var y = d3.scale.linear().range([svgRect.height - 15, 0]);

  // Define the axes
  var xAxis = d3.svg.axis().scale(x)
      .ticks(4)
      .tickFormat(function(d) { return timeFormat(new Date(data[d].x)); })
      .orient('bottom');

  // Define the line
  var valueline = d3.svg.line()
      .x(function(d, i) { return x(i); })
      .y(function(d) { return y(d.y); })
      // .defined(function(d) { return !d.failed; });


  // Scale the range of the data
  x.domain(d3.extent(data, function(d, i) { return i; }));
  y.domain([0, d3.max(data, function(d) { return d.y; })]);

  // Add the valueline path.
  svg.append('path')
      .attr('class', 'line')
      .attr('d', valueline(data));

  // Add the X Axis
  svg.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(0,' +( svgRect.height - 15) + ')')
      .call(xAxis);

  // // Add the Y Axis
  // svg.append("g")
  //     .attr("class", "y axis")
  //     .call(yAxis);

};
