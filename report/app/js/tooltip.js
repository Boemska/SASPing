/* eslint-env node, browser */
/* globals d3 */

var timeFormat = d3.time.format('%d-%m-%y %H:%M');

var tooltip = d3.select('#app-table')
                .append('div')
                .attr('class', 'tooltip');

tooltip.append('div')
       .attr('class', 'request-id');

tooltip.append('div')
       .attr('class', 'time');

tooltip.append('div')
       .attr('class', 'duration');


module.exports = {
  setAppChartData: function(id, time, duration) {
    tooltip.select('.request-id').html('<b>ID</b>: ' + id);
    tooltip.select('.time').html('<b>Date</b>: ' + timeFormat(time));
    tooltip.select('.duration').html('<b>Duration</b>: ' + (duration / 1000) + ' seconds');
    return this;
  },
  show: function(top, left) {
    var tooltipRect = tooltip.node().getBoundingClientRect();
    tooltip.style('top', (top - tooltipRect.height - 5) + 'px');
    tooltip.style('left', (left - tooltipRect.width / 2) + 'px');
    tooltip.style('visibility', 'visible');
    return this;
  },
  hide: function() {
    tooltip.style('visibility', null);
    return this;
  }
};
