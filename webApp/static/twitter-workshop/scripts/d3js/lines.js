// parse the date / time


    // Get the data
    function draw(data, type) {

        // set the dimensions and margins of the graph
        var margin = {top: 5, right: 5, bottom: 35, left: 40},
            width = $(".line-chart").width() - margin.left - margin.right,
            height = $(".line-chart").height() - margin.top - margin.bottom;


        // set the ranges
        var x = d3.scaleTime().range([0, width]);
        var y = d3.scaleLinear().range([height, 0]);

        var yAxis = d3.axisRight(y)
            .tickSize(width)
            .ticks(2);

        var xAxis = d3.axisBottom(x)
            .tickFormat(d3.timeFormat("%H:%M"));

        var bisect = d3.bisector(function(d) {
            return d.current_timeframe;
        }).left;


        var tooltip = d3.select('.line-chart')
            .append('div')
            .attr('class', 'tooltip');

        // append the svg obgect to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        var svg = d3.select(".line-chart svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        // define the 1st line
        valueline = d3.line()
            .x(function(d) { return x(d.current_timeframe); })
            .y(function(d) { return y(d["previous_" + type + "_count"]); });

        // define the 2nd line
        valueline2 = d3.line()
            .x(function(d) { return x(d.current_timeframe); })
            .y(function(d) { return y(d["current_" + type + "_count"]); });

        // Scale the range of the data
        x.domain(d3.extent(data, function(d) { return d.current_timeframe; }));
        y.domain([0, d3.max(data, function(d) {
            return Math.max(d["previous_" + type + "_count"] , d["current_" + type + "_count"] ); })]);

        // Add the X Axis
        svg.append("g")
            .call(customXAxis);

        // Add the Y Axis
        svg.append("g")
            .call(customYAxis);

        // Add the valueline path.
        svg.append("path")
            .data([data])
            .attr("class", "line previous")
            .style("stroke-dasharray", ("5, 5"))
            .style("opacity", 0.5)
            .style("stroke", "#3498db")
            .style("stroke-width", "1")
            .style("fill", "none")
            .attr("d", valueline);

        // Add the valueline2 path.
        svg.append("path")
            .data([data])
            .attr("class", "line current")
            .style("stroke", "#3498db")
            .style("stroke-width", "1")
            .style("fill", "none")
            .attr("d", valueline2);

        svg.selectAll("dot")
            .data(data)
            .enter().append("circle")
            .attr("r", 3)
            .attr("fill", "#2980b9")
            .style("opacity", 1)
            .attr("cx", function(d) { return x(d.current_timeframe); })
            .attr("cy", function(d) { return y(d["current_" + type + "_count"]); });
        svg.selectAll("dot")
            .data(data)
            .enter().append("circle")
            .attr("r", 3)
            .style("opacity", 0.5)
            .attr("fill", "#2980b9")
            .attr("cx", function(d) { return x(d.current_timeframe); })
            .attr("cy", function(d) { return y(d["previous_" + type + "_count"]); });
        var chartArea = svg.append('rect')
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', width)
            .attr('height', height)
            .style('fill', 'none')
            .style('pointer-events', 'all');

        chartArea
            .on("mouseover", function() {
                d3.select(".svg-line-marker")
                    .transition()
                    .duration(105)
                    .style("opacity", 20)
                    .style("stroke-width", 2);
                d3.select(".svg-line-marker-line")
                    .transition().duration(105)
                    .style("opacity", 20).style("stroke-width", 2);

                d3.select(".tooltip")
                    .transition().duration(105)
                    .style("opacity", 1);

                var mouse = d3.mouse(this);var xPos = mouse[0];
                var x0 = x.invert(xPos - 20);
                var i = bisect(data, x0);var d = data[i];
            })
            .on("mouseout", function() {

                d3.select(".svg-line-marker")
                    .transition().duration(105)
                    .style("opacity", 0).style("stroke-width", 0.5);

                d3.select(".svg-line-marker-line")
                    .transition().duration(105)
                    .style("opacity", 0).style("stroke-width", 0.5);

                d3.select(".tooltip")
                    .transition().duration(105)
                    .style("opacity", 0);

                var mouse = d3.mouse(this);var xPos = mouse[0];
                var x0 = x.invert(xPos - 20);
                var i = bisect(data, x0);var d = data[i];

            })
            .on("mousemove", function() {
                var mouse = d3.mouse(this);
                var xPos = mouse[0];
                var x0 = x.invert(xPos - 20);
                var i = bisect(data, x0);

                var d = data[i];
                if (d) {
                    var xp = x(d.current_timeframe) + 20;
                    var yp = y(d["current_" + type + "_count"]) + 20;

                    current_date = new Date(Date.parse(d.current_timeframe));
                    previous_date = new Date(Date.parse(d.current_timeframe));

                    d3.select('.tooltip').html( '<span class="value"><svg height="8" width="16"><line x1="0" y1="4" x2="16" y2="4" style="stroke:#3498db;stroke-width:1" /></svg>' + d["current_" + type + "_count"] + " </span>" + current_date.getFullYear() + "-" + ((current_date.getDate()+1)<10?'0':'') + (current_date.getDate()) + "-" + (current_date.getDate()<10?'0':'') + current_date.getDate() + " " + (current_date.getHours()<10?'0':'') + current_date.getHours() + ":" + (current_date.getMinutes()<10?'0':'') + current_date.getMinutes() + "" +
                        '<br /><span class="value"><svg height="8" width="16"><line x1="0" y1="4" x2="16" y2="4" style="stroke:#3498db;stroke-width:1;stroke-dasharray:3,1" /></svg>' + d["previous_" + type + "_count"] + " </span>" + previous_date.getFullYear() + "-" + ((previous_date.getDate()+1)<10?'0':'') + (previous_date.getDate()) + "-" + (previous_date.getDate()<10?'0':'') + previous_date.getDate() + " " + (previous_date.getHours()<10?'0':'') + previous_date.getHours() + ":" + (previous_date.getMinutes()<10?'0':'') + previous_date.getMinutes() + "");
                    d3.select('.tooltip')
                        .style('left', (xp) - 46 +'px')
                        .style('top', (yp + 89) +'px');

                    d3.select('.svg-line-marker')
                        .style('opacity', 20).attr('transform', 'translate('+xp+', '+yp+')');
                    d3.select('.svg-line-marker-line')
                        .attr('y1', yp)
                        .attr('x1', xp)
                        .attr('x2', xp);
                }
            });

        function customYAxis(g) {
            g.call(yAxis);
            g.select(".domain").remove();
            g.selectAll(".tick:first-of-type line").attr("stroke", "#e6ebec");
            g.selectAll(".tick:not(:first-of-type) line").attr("stroke", "#ecf0f1");
            g.selectAll(".tick text").attr("x", -10).attr("text-anchor", "end").attr("dy", 3);
        }

        function customXAxis(g) {
            g.call(xAxis);
            g.select(".domain").remove();
            g.attr("class", "x-axis");
            g.attr('transform', 'translate(0,' + (height) + ')');
            g.selectAll(".tick text").attr("dy", 10);
        }
    }