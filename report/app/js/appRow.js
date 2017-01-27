/* eslint-env node, browser */
/* globals d3 */
module.exports = function(ledColor, appName, data) {
  var tooltip = require('./tooltip.js');

  var row = d3.select('#app-table')
      .append('div').attr('class', 'row app-row card')
        .append('div').attr('class', 'row-content align-children');
  row.append('div')
        .append('div').attr('class', 'led center-table led-' + ledColor);
  row.append('div')
        .append('p').text(appName);

  var svgWrapper = row.append('div');
  var svg = svgWrapper.append('svg')
                      .attr('class', 'sparkline');


  function draw() {
    // clean svg element for redraw
    svg.node().innerHTML = '';
    var svgWrapperRect = svgWrapper.node().getBoundingClientRect();

    if(svgWrapperRect.width > 400) {
      svg.attr('width', svgWrapperRect.width - 100);
      svg.style('margin', '0 50px');
    } else {
      svg.attr('width', svgWrapperRect.width);
      svg.style('margin', '0 0');
    }

    var svgRect = svg.node().getBoundingClientRect();

    var timeFormat;
    if(data[0].x - data[data.length-1].x > 24 * 60 * 60 * 1000) {
      timeFormat = d3.time.format('%d-%m-%y');
    } else {
      timeFormat = d3.time.format('%H:%M');
    }


    // Set the ranges
    var x = d3.scale.linear().range([svgRect.width - 15, 0]);
    var y = d3.scale.linear().range([svgRect.height - 15, 0]);

    // Define the axes
    var xAxis = d3.svg.axis().scale(x)
        .ticks(2)
        .tickFormat(function(d) { return timeFormat(new Date(data[d].x)); })
        .orient('bottom');

    // Define the line
    var valueline = d3.svg.line()
        .x(function(d, i) { return x(i); })
        .y(function(d) { return y(d.y); })
        .defined(function(d) { return !d.failed; });


    // Scale the range of the data
    x.domain(d3.extent(data, function(d, i) { return i; }));
    y.domain([0, d3.max(data, function(d) {
      // failed request running more than 10 seconds are ignored
      return d.failed && d.y > 10000 ? 0 : d.y;
    })]);

    // Add the valueline path.
    svg.append('path')
        .attr('class', 'line')
        .attr('d', valueline(data));

    // Add the scatterplot
    svg.selectAll('dot')
        .data(data)
          .enter().append('circle')
          .attr('r', 2.6)
          .attr('cx', function(d, i) { return x(i); })
          .attr('cy', function(d) {
            // failed request running more than 10 seconds are moved to x axis
            return d.failed && d.y > 10000 ? y(0) : y(d.y);
          })
          .style('fill', function(d) {
            return d.failed === true ? 'red' : null;
          })
          .on('mouseover', function(d) {
            d3.select(this).attr('r', 6);
            var clientRect = this.getBoundingClientRect();
            tooltip.setAppChartData(d.id, new Date(d.x), d.y).show(clientRect.top, clientRect.left);
          })
          .on('mouseout', function() {
            d3.select(this).attr('r', 2.6);
            tooltip.hide();
          });

    // Add the X Axis
    svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' +( svgRect.height - 15) + ')')
        .call(xAxis);
  }

  draw();

  function resizeThrottler() {
    var timeout;
    return function() {
      if(!timeout) {
        timeout = setTimeout(function() {
          timeout = null;
          draw();
        }, 100);
      }
    };
  }

  window.addEventListener('resize', resizeThrottler());
};
