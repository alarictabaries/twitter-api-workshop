function show_info(d) {
    if(d == false) {
        $(".card.node").fadeOut(85);
    } else {
        $(".card.node .pic").attr("src", "https://avatars.io/twitter/" + d.alias + "/small");
        $(".card.node .alias").html("<a target=\"_BLANK\" href=\"https://twitter.com/intent/user?user_id=" + d.id_str + "\">@" + d.alias + "</a>");
        $(".card.node .freq").html("<span class=\"label\">Mentioned</span><br />" + d.freq);
        $(".card.node").fadeIn(115);
    }
}

function update_interactions(threshold, lonely_nodes, token) {
    $('#overlay').fadeIn(125);
    show_info(false);
    $.ajax({
        type: "POST",
        url: '/update_interactions?id=' + getUrlVars()["id"],
        data: {
            csrfmiddlewaretoken: token,
            threshold: threshold
        },
        success: function (response) {
            var data_set = response[0];
            svg = d3.select('.graph').append("svg");
            createV4SelectableForceDirectedGraph(svg, data_set, most_engaged_nodes);
        },
        complete: function(){
            $('#overlay').fadeOut(125);
        }
    });
}

function createV4SelectableForceDirectedGraph(svg, graph, most_engaged_nodes) {
    // if both d3v3 and d3v4 are loaded, we'll assume
    // that d3v4 is called d3v4, otherwise we'll assume
    // that d3v4 is the default (d3)

    graph.nodes = graph.nodes.reverse();

    $(".settings .data .nodes").html("Nodes: " + graph.nodes.length);
    $(".settings .data .links").html("Links analyzed: " + graph.links.length);

    defs = svg.append("defs");

    for(node in most_engaged_nodes) {
        defs.append("pattern").attr("id", most_engaged_nodes[node]["alias"]).attr("viewBox", "0 0 1 1").attr("patternUnits", "objectBoundingBox").attr("preserveAspectRatio", "xMidYMid slice").attr("height", 1).attr("width", 1)
            .append("image").attr("height",1).attr("width",1).attr("preserveAspectRatio", "xMidYMid slice").attr("xlink:href",most_engaged_nodes[node]["profile_picture_url"])
    }

    if (typeof d3v4 == 'undefined')
        d3v4 = d3;

    var width = +svg.attr("width"),
        height = +svg.attr("height");

    let parentWidth = d3v4.select('svg').node().parentNode.clientWidth;
    let parentHeight = d3v4.select('svg').node().parentNode.clientHeight;

    var svg = d3v4.select('svg')
        .attr('width', parentWidth)
        .attr('height', parentHeight)

    // remove any previous graphs
    svg.selectAll('.g-main').remove();

    var gMain = svg.append('g')
        .classed('g-main', true);

    var rect = gMain.append('rect')
        .attr('width', parentWidth)
        .attr('height', parentHeight)
        .style('fill', 'white')

    var gDraw = gMain.append('g');

    var zoom = d3v4.zoom()
        .on('zoom', zoomed)

    gMain.call(zoom);

    function zoomed() {
        gDraw.attr('transform', d3v4.event.transform);
    }

    var color = d3v4.scaleOrdinal(d3v4.schemeCategory20);

    if (! ("links" in graph)) {
        console.log("Graph is missing links");
        return;
    }

    var nodes = {};
    var i;
    for (i = 0; i < graph.nodes.length; i++) {
        nodes[graph.nodes[i].id] = graph.nodes[i];
        graph.nodes[i].weight = 1.01;
    }

    // the brush needs to go before the nodes so that it doesn't
    // get called when the mouse is over a node
    var gBrushHolder = gDraw.append('g');
    var gBrush = null;

    var link = gDraw.append("g")
        .attr("class", "link")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

    // Dirty method to hide unlinked circles, work needed on it, filter before append?
    var node = gDraw.append("g")
        .attr("class", "node")
        .selectAll("circle")
        .data(graph.nodes)
        .enter()
        .append("circle")
        .attr("r", function(d) {
            return Math.sqrt((d.freq+1)*3.14);
        })
        .attr("class", function(d) {
            for(i in most_engaged_nodes) {
                if(d.id_str == most_engaged_nodes[i]["id_str"]) {
                    return("influencer");
                }
            }
            if (d.type == 1) {
                return ("active");
            } else {
                return ("inactive");
            }
        })
        .attr("fill", function(d) {
            for(i in most_engaged_nodes) {
                if(d.id_str == most_engaged_nodes[i]["id_str"]) {
                    return "url(#" + d.alias + ")";
                }
            }
            if ('color' in d)
                return d.color;
            else
                return color(d.group);
        })
        .call(d3v4.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    /*$("circle.void").remove();*/

    // add titles for mouseover blurbs
    node.append("title").attr("class", "label")
        .text(function(d) {
            if ('alias' in d)
                return "@" + d.alias;
            else
                return d.id;
        });

    var simulation = d3v4.forceSimulation()
        .force("link", d3v4.forceLink()
            .id(function(d) { return d.id; })
            .distance(function(d) {
                //return 30;
                var dist = (d.value);
                //console.log('dist:', dist);

                return dist;
            })
        )
        .force("charge", d3v4.forceManyBody())
        // if nodes < X,
        //.force("charge", d3v4.forceManyBody().strength(-160))
        .force("center", d3v4.forceCenter(parentWidth / 2, parentHeight / 2))
        .force("x", d3v4.forceX(parentWidth/2))
        .force("y", d3v4.forceY(parentHeight/2));

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
        // update node and line positions at every step of
        // the force simulation
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
    }

    var brushMode = false;
    var brushing = false;

    var brush = d3v4.brush()
        .on("start", brushstarted)
        .on("brush", brushed)
        .on("end", brushended);

    function brushstarted() {
        // keep track of whether we're actively brushing so that we
        // don't remove the brush on keyup in the middle of a selection
        brushing = true;

        node.each(function(d) {
            d.previouslySelected = shiftKey && d.selected;
        });
    }

    rect.on('click', () => {
        show_info(false);
        d3v4.selectAll("line").attr("class", "link");
        node.each(function(d) {
            d.selected = false;
            d.previouslySelected = false;
        });
        node.classed("selected", false);
    });

    function brushed() {
        if (!d3v4.event.sourceEvent) return;
        if (!d3v4.event.selection) return;

        var extent = d3v4.event.selection;

        node.classed("selected", function(d) {
            return d.selected = d.previouslySelected ^
                (extent[0][0] <= d.x && d.x < extent[1][0]
                    && extent[0][1] <= d.y && d.y < extent[1][1]);
        });
    }

    function brushended() {
        if (!d3v4.event.sourceEvent) return;
        if (!d3v4.event.selection) return;
        if (!gBrush) return;

        gBrush.call(brush.move, null);

        if (!brushMode) {
            // the shift key has been release before we ended our brushing
            gBrush.remove();
            gBrush = null;
        }

        brushing = false;
    }

    d3v4.select('body').on('keydown', keydown);
    d3v4.select('body').on('keyup', keyup);

    var shiftKey;

    function keydown() {
        shiftKey = d3v4.event.shiftKey;

        /* Removing shiftkey functionality

        if (shiftKey) {
            // if we already have a brush, don't do anything
            if (gBrush)
                return;
            brushMode = true;

            if (!gBrush) {
                gBrush = gBrushHolder.append('g');
                gBrush.call(brush);
            }
        }*/
    }

    function keyup() {
        shiftKey = false;
        brushMode = false;

        if (!gBrush)
            return;

        if (!brushing) {
            // only remove the brush if we're not actively brushing
            // otherwise it'll be removed when the brushing ends
            gBrush.remove();
            gBrush = null;
        }
    }

    function dragstarted(d) {
        if (!d3v4.event.active) simulation.alphaTarget(0.9).restart();

        if (!d.selected && !shiftKey) {
            // if this node isn't selected, then we have to unselect every other node
            node.classed("selected", function(p) { return p.selected =  p.previouslySelected = false; });
        }

        d3v4.select(this).classed("selected", function(p) {show_info(d); d.previouslySelected = d.selected; return d.selected = true; });
        nodeObj = d;
        d3v4.selectAll("line").attr("class", "link");
        d3v4.selectAll("line").filter(function(d) {
             return (d.source === nodeObj) || (d.target === nodeObj);
           })
          .attr("class", "hl")

        node.filter(function(d) {
            return d.selected;
        })
            .each(function(d) { //d.fixed |= 2;
                d.fx = d.x;
                d.fy = d.y;
            })

    }

    function dragged(d) {
        //d.fx = d3v4.event.x;
        //d.fy = d3v4.event.y;
        node.filter(function(d) { return d.selected; })
            .each(function(d) {
                d.fx += d3v4.event.dx;
                d.fy += d3v4.event.dy;
            })
    }

    function dragended(d) {
        if (!d3v4.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
        node.filter(function(d) { return d.selected; })
            .each(function(d) { //d.fixed &= ~6;
                d.fx = null;
                d.fy = null;
            })
    }

    return graph;
};