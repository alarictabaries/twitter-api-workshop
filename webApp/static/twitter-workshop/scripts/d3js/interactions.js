function show_info(d) {
	if (d == false) {
		$(".card.node").fadeOut(85);
	} else {
		$(".card.node").fadeOut(85);
		$.ajax({
			headers: {
				"X-CSRFToken": getCookie("csrftoken")
			},
			type: "POST",
			url: '/app/get_user_details/',
			data: {
				_id: d.id_str,
			},
			success: function(response) {},
			complete: function(response) {
				$(".card.node .pic").attr("src", response.responseJSON.profile_image_url_https);
				$(".card.node .name").html(response.responseJSON.name);
				$(".card.node .screen_name").html("<a target=\"_BLANK\" href=\"https://twitter.com/intent/user?user_id=" + d.id_str + "\">@" + response.responseJSON.screen_name + "</a>");
				$(".card.node .followers").html("<span class=\"label\">Followers</span><br /><span class=\"count\">" + numberWithSpaces(response.responseJSON.followers_count) + "</span>");
				$(".card.node .mentions").html("<span class=\"label\">Mentions</span><br /><span class=\"count\">" + d.mentions + "</span>");
				$(".card.node").fadeIn(85);
			}
		});
	}
}

function createV4SelectableForceDirectedGraph(svg, graph, most_engaged_nodes) {
	// if both d3v3 and d3v4 are loaded, we'll assume
	// that d3v4 is called d3v4, otherwise we'll assume
	// that d3v4 is the default (d3)
	graph.nodes = graph.nodes.reverse();
	$(".settings .data .nodes").html("Nodes: " + graph.nodes.length);
	$(".settings .data .links").html("Links analyzed: " + graph.links.length);
	defs = svg.append("defs");
	for (node in most_engaged_nodes) {
		defs.append("pattern").attr("id", most_engaged_nodes[node]["id_str"]).attr("viewBox", "0 0 1 1").attr("patternUnits", "objectBoundingBox").attr("preserveAspectRatio", "xMidYMid slice").attr("height", 1).attr("width", 1).append("image").attr("height", 1).attr("width", 1).attr("preserveAspectRatio", "xMidYMid slice").attr("xlink:href", most_engaged_nodes[node]["profile_image_url"])
	}
	if (typeof d3v4 == 'undefined') d3v4 = d3;
	var width = +svg.attr("width"),
		height = +svg.attr("height");
	let parentWidth = d3v4.select('svg').node().parentNode.clientWidth;
	let parentHeight = d3v4.select('svg').node().parentNode.clientHeight;
	var svg = d3v4.select('svg').attr('width', parentWidth).attr('height', parentHeight)
	// remove any previous graphs
	svg.selectAll('.g-main').remove();
	var gMain = svg.append('g').classed('g-main', true);
	var rect = gMain.append('rect').attr('width', parentWidth).attr('height', parentHeight).style('fill', 'white')
	var gDraw = gMain.append('g');
	var zoom = d3v4.zoom().on('zoom', zoomed)
	gMain.call(zoom);

Colors = {};
Colors.names = {
    aqua: "#00ffff",
    azure: "#f0ffff",
    beige: "#f5f5dc",
    black: "#000000",
    blue: "#0000ff",
    brown: "#a52a2a",
    cyan: "#00ffff",
    darkblue: "#00008b",
    darkcyan: "#008b8b",
    darkgrey: "#a9a9a9",
    darkgreen: "#006400",
    darkkhaki: "#bdb76b",
    darkmagenta: "#8b008b",
    darkolivegreen: "#556b2f",
    darkorange: "#ff8c00",
    darkorchid: "#9932cc",
    darkred: "#8b0000",
    darksalmon: "#e9967a",
    darkviolet: "#9400d3",
    fuchsia: "#ff00ff",
    gold: "#ffd700",
    green: "#008000",
    indigo: "#4b0082",
    khaki: "#f0e68c",
    lightblue: "#add8e6",
    lightcyan: "#e0ffff",
    lightgreen: "#90ee90",
    lightgrey: "#d3d3d3",
    lightpink: "#ffb6c1",
    lightyellow: "#ffffe0",
    lime: "#00ff00",
    magenta: "#ff00ff",
    maroon: "#800000",
    navy: "#000080",
    olive: "#808000",
    orange: "#ffa500",
    pink: "#ffc0cb",
    purple: "#800080",
    violet: "#800080",
    red: "#ff0000",
    silver: "#c0c0c0",
    white: "#ffffff",
    yellow: "#ffff00"
};

Colors.random = function(value) {
        var result;
        var count = 0;
        for (var prop in this.names)
            if (value/100 < 1/++count)
               result = prop;
        return { name: result, rgb: this.names[result]};
    };

	function zoomed() {
		gDraw.attr('transform', d3v4.event.transform);
	}
	var color = d3v4.scaleOrdinal(d3v4.schemeCategory20);
	if (!("links" in graph)) {
		console.log("Graph is missing links");
		return;
	}
	var nodes = {};
	var i;
	for (i = 0; i < graph.nodes.length; i++) {
		nodes[graph.nodes[i].id_str] = graph.nodes[i];
		graph.nodes[i].weight = 1.01;
	}
	// the brush needs to go before the nodes so that it doesn't
	// get called when the mouse is over a node
	var gBrushHolder = gDraw.append('g');
	var gBrush = null;
	var link = gDraw.append("g").attr("class", "link").selectAll("line").data(graph.links).enter().append("line").attr("stroke-width", function(d) {
		return Math.sqrt(d.value);
	});
	// Dirty method to hide unlinked circles, work needed on it, filter before append?
	var node = gDraw.append("g").attr("class", "node").selectAll("circle").data(graph.nodes).enter().append("circle").attr("r", function(d) {
		return Math.sqrt((d.mentions + 1) * 3.14);
	}).attr("id", function(d) {
		return d.id_str
	}).attr("class", function(d) {
		for (i in most_engaged_nodes) {
			if (d.id_str == most_engaged_nodes[i]["id_str"]) {
				if (d.type == 1) {
					return ("influencer_active influencer");
				} else {
					return ("influencer_inactive influencer");
				}
			}
		}
		if (d.type == 1) {
			return ("active");
		} else {
			return ("inactive");
		}
	}).attr("fill", function(d) {
		for (i in most_engaged_nodes) {
			if (d.id_str == most_engaged_nodes[i]["id_str"]) {
				return "url(#" + d.id_str + ")";
			}
		}
		if ('community' in d) return Colors.random(d.community).rgb;
		else return color(d.group);
	}).call(d3v4.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));
	/*$("circle.void").remove();*/
	// add titles for mouseover blurbs
	/*node.append("title").attr("class", "label")
	    .text(function(d) {
	        if ('screen_name' in d)
	            return "@" + d.screen_name;
	        else
	            return d.id;
	    });*/
	var simulation = d3v4.forceSimulation().force("link", d3v4.forceLink().id(function(d) {
			return parseInt(d.id_str);
		}).distance(function(d) {
			return 30;
			// var dist = (d.value);
			// return dist;
		}))
		//.force("charge", d3v4.forceManyBody())
		.force("charge", d3v4.forceManyBody().strength(-30)).force("center", d3v4.forceCenter(parentWidth / 2, parentHeight / 2)).force("x", d3v4.forceX(parentWidth / 2)).force("y", d3v4.forceY(parentHeight / 2));
	simulation.nodes(graph.nodes).on("tick", ticked);
	simulation.force("link").links(graph.links);

	function ticked() {
		// update node and line positions at every step of
		// the force simulation
		link.attr("x1", function(d) {
			return d.source.x;
		}).attr("y1", function(d) {
			return d.source.y;
		}).attr("x2", function(d) {
			return d.target.x;
		}).attr("y2", function(d) {
			return d.target.y;
		});
		node.attr("cx", function(d) {
			return d.x;
		}).attr("cy", function(d) {
			return d.y;
		});
	}
	var brushMode = false;
	var brushing = false;
	var brush = d3v4.brush().on("start", brushstarted).on("brush", brushed).on("end", brushended);

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
			return d.selected = d.previouslySelected ^ (extent[0][0] <= d.x && d.x < extent[1][0] && extent[0][1] <= d.y && d.y < extent[1][1]);
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
		if (!gBrush) return;
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
			node.classed("selected", function(p) {
				return p.selected = p.previouslySelected = false;
			});
		}
		d3v4.select(this).classed("selected", function(p) {
			show_info(d);
			d.previouslySelected = d.selected;
			return d.selected = true;
		});
		nodeObj = d;
		d3v4.selectAll("line").attr("class", "link");
		d3v4.selectAll("line").filter(function(d) {
			return (d.source === nodeObj) || (d.target === nodeObj);
		}).attr("class", "highlight")
		node.filter(function(d) {
			return d.selected;
		}).each(function(d) { //d.fixed |= 2;
			d.fx = d.x;
			d.fy = d.y;
		})
	}

	function dragged(d) {
		//d.fx = d3v4.event.x;
		//d.fy = d3v4.event.y;
		node.filter(function(d) {
			return d.selected;
		}).each(function(d) {
			d.fx += d3v4.event.dx;
			d.fy += d3v4.event.dy;
		})
	}

	function dragended(d) {
		if (!d3v4.event.active) simulation.alphaTarget(0);
		d.fx = null;
		d.fy = null;
		node.filter(function(d) {
			return d.selected;
		}).each(function(d) { //d.fixed &= ~6;
			d.fx = null;
			d.fy = null;
		})
	}
	return graph;
};

(function (global, factory) {
            typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('d3-dispatch'), require('d3-drag'), require('d3-interpolate'), require('d3-selection'), require('d3-transition')) :
                typeof define === 'function' && define.amd ? define(['exports', 'd3-dispatch', 'd3-drag', 'd3-interpolate', 'd3-selection', 'd3-transition'], factory) :
                    (factory((global.d3 = global.d3 || {}),global.d3,global.d3,global.d3,global.d3,global.d3));
        }(this, (function (exports,d3Dispatch,d3Drag,d3Interpolate,d3Selection,d3Transition) { 'use strict';

            var constant = function(x) {
                return function() {
                    return x;
                };
            };

            var BrushEvent = function(target, type, selection) {
                this.target = target;
                this.type = type;
                this.selection = selection;
            };

            function nopropagation() {
                d3Selection.event.stopImmediatePropagation();
            }

            var noevent = function() {
                d3Selection.event.preventDefault();
                d3Selection.event.stopImmediatePropagation();
            };

            var MODE_DRAG = {name: "drag"};
            var MODE_SPACE = {name: "space"};
            var MODE_HANDLE = {name: "handle"};
            var MODE_CENTER = {name: "center"};

            var X = {
                name: "x",
                handles: ["e", "w"].map(type),
                input: function(x, e) { return x && [[x[0], e[0][1]], [x[1], e[1][1]]]; },
                output: function(xy) { return xy && [xy[0][0], xy[1][0]]; }
            };

            var Y = {
                name: "y",
                handles: ["n", "s"].map(type),
                input: function(y, e) { return y && [[e[0][0], y[0]], [e[1][0], y[1]]]; },
                output: function(xy) { return xy && [xy[0][1], xy[1][1]]; }
            };

            var XY = {
                name: "xy",
                handles: ["n", "e", "s", "w", "nw", "ne", "se", "sw"].map(type),
                input: function(xy) { return xy; },
                output: function(xy) { return xy; }
            };

            var cursors = {
                overlay: "crosshair",
                selection: "move",
                n: "ns-resize",
                e: "ew-resize",
                s: "ns-resize",
                w: "ew-resize",
                nw: "nwse-resize",
                ne: "nesw-resize",
                se: "nwse-resize",
                sw: "nesw-resize"
            };

            var flipX = {
                e: "w",
                w: "e",
                nw: "ne",
                ne: "nw",
                se: "sw",
                sw: "se"
            };

            var flipY = {
                n: "s",
                s: "n",
                nw: "sw",
                ne: "se",
                se: "ne",
                sw: "nw"
            };

            var signsX = {
                overlay: +1,
                selection: +1,
                n: null,
                e: +1,
                s: null,
                w: -1,
                nw: -1,
                ne: +1,
                se: +1,
                sw: -1
            };

            var signsY = {
                overlay: +1,
                selection: +1,
                n: -1,
                e: null,
                s: +1,
                w: null,
                nw: -1,
                ne: -1,
                se: +1,
                sw: +1
            };

            function type(t) {
                return {type: t};
            }

// Ignore right-click, since that should open the context menu.
            function defaultFilter() {
                return !d3Selection.event.button;
            }

            function defaultExtent() {
                var svg = this.ownerSVGElement || this;
                return [[0, 0], [svg.width.baseVal.value, svg.height.baseVal.value]];
            }

// Like d3.local, but with the name “__brush” rather than auto-generated.
            function local(node) {
                while (!node.__brush) if (!(node = node.parentNode)) return;
                return node.__brush;
            }

            function empty(extent) {
                return extent[0][0] === extent[1][0]
                    || extent[0][1] === extent[1][1];
            }

            function brushSelection(node) {
                var state = node.__brush;
                return state ? state.dim.output(state.selection) : null;
            }

            function brushX() {
                return brush$1(X);
            }

            function brushY() {
                return brush$1(Y);
            }

            var brush = function() {
                return brush$1(XY);
            };

            function brush$1(dim) {
                var extent = defaultExtent,
                    filter = defaultFilter,
                    listeners = d3Dispatch.dispatch(brush, "start", "brush", "end"),
                    handleSize = 6,
                    touchending;

                function brush(group) {

                    var overlay = group
                        .property("__brush", initialize)
                        .selectAll(".overlay")
                        .data([type("overlay")]);

                    overlay.enter().append("rect")
                        .attr("class", "overlay")
                        .attr("pointer-events", "all")
                        .attr("cursor", cursors.overlay)
                        .merge(overlay)
                        .each(function() {
                            var extent = local(this).extent;
                            d3Selection.select(this)
                                .attr("x", extent[0][0])
                                .attr("y", extent[0][1])
                                .attr("width", extent[1][0] - extent[0][0])
                                .attr("height", extent[1][1] - extent[0][1]);
                        });

                    group.selectAll(".selection")
                        .data([type("selection")])
                        .enter().append("rect")
                        .attr("class", "selection")
                        .attr("cursor", cursors.selection)
                        .attr("fill", "#777")
                        .attr("fill-opacity", 0.3)
                        .attr("stroke", "#fff")
                        .attr("shape-rendering", "crispEdges");

                    var handle = group.selectAll(".handle")
                        .data(dim.handles, function(d) { return d.type; });

                    handle.exit().remove();

                    handle.enter().append("rect")
                        .attr("class", function(d) { return "handle handle--" + d.type; })
                        .attr("cursor", function(d) { return cursors[d.type]; });

                    group
                        .each(redraw)
                        .attr("fill", "none")
                        .attr("pointer-events", "all")
                        .style("-webkit-tap-highlight-color", "rgba(0,0,0,0)")
                        .on("mousedown.brush touchstart.brush", started);
                }

                brush.move = function(group, selection) {
                    if (group.selection) {
                        group
                            .on("start.brush", function() { emitter(this, arguments).beforestart().start(); })
                            .on("interrupt.brush end.brush", function() { emitter(this, arguments).end(); })
                            .tween("brush", function() {
                                var that = this,
                                    state = that.__brush,
                                    emit = emitter(that, arguments),
                                    selection0 = state.selection,
                                    selection1 = dim.input(typeof selection === "function" ? selection.apply(this, arguments) : selection, state.extent),
                                    i = d3Interpolate.interpolate(selection0, selection1);

                                function tween(t) {
                                    state.selection = t === 1 && empty(selection1) ? null : i(t);
                                    redraw.call(that);
                                    emit.brush();
                                }

                                return selection0 && selection1 ? tween : tween(1);
                            });
                    } else {
                        group
                            .each(function() {
                                var that = this,
                                    args = arguments,
                                    state = that.__brush,
                                    selection1 = dim.input(typeof selection === "function" ? selection.apply(that, args) : selection, state.extent),
                                    emit = emitter(that, args).beforestart();

                                d3Transition.interrupt(that);
                                state.selection = selection1 == null || empty(selection1) ? null : selection1;
                                redraw.call(that);
                                emit.start().brush().end();
                            });
                    }
                };

                function redraw() {
                    var group = d3Selection.select(this),
                        selection = local(this).selection;

                    if (selection) {
                        group.selectAll(".selection")
                            .style("display", null)
                            .attr("x", selection[0][0])
                            .attr("y", selection[0][1])
                            .attr("width", selection[1][0] - selection[0][0])
                            .attr("height", selection[1][1] - selection[0][1]);

                        group.selectAll(".handle")
                            .style("display", null)
                            .attr("x", function(d) { return d.type[d.type.length - 1] === "e" ? selection[1][0] - handleSize / 2 : selection[0][0] - handleSize / 2; })
                            .attr("y", function(d) { return d.type[0] === "s" ? selection[1][1] - handleSize / 2 : selection[0][1] - handleSize / 2; })
                            .attr("width", function(d) { return d.type === "n" || d.type === "s" ? selection[1][0] - selection[0][0] + handleSize : handleSize; })
                            .attr("height", function(d) { return d.type === "e" || d.type === "w" ? selection[1][1] - selection[0][1] + handleSize : handleSize; });
                    }

                    else {
                        group.selectAll(".selection,.handle")
                            .style("display", "none")
                            .attr("x", null)
                            .attr("y", null)
                            .attr("width", null)
                            .attr("height", null);
                    }
                }

                function emitter(that, args) {
                    return that.__brush.emitter || new Emitter(that, args);
                }

                function Emitter(that, args) {
                    this.that = that;
                    this.args = args;
                    this.state = that.__brush;
                    this.active = 0;
                }

                Emitter.prototype = {
                    beforestart: function() {
                        if (++this.active === 1) this.state.emitter = this, this.starting = true;
                        return this;
                    },
                    start: function() {
                        if (this.starting) this.starting = false, this.emit("start");
                        return this;
                    },
                    brush: function() {
                        this.emit("brush");
                        return this;
                    },
                    end: function() {
                        if (--this.active === 0) delete this.state.emitter, this.emit("end");
                        return this;
                    },
                    emit: function(type) {
                        d3Selection.customEvent(new BrushEvent(brush, type, dim.output(this.state.selection)), listeners.apply, listeners, [type, this.that, this.args]);
                    }
                };

                function started() {
                    if (d3Selection.event.touches) { if (d3Selection.event.changedTouches.length < d3Selection.event.touches.length) return noevent(); }
                    else if (touchending) return;
                    if (!filter.apply(this, arguments)) return;

                    var that = this,
                        type = d3Selection.event.target.__data__.type,
                        mode = (d3Selection.event.metaKey ? type = "overlay" : type) === "selection" ? MODE_DRAG : (d3Selection.event.altKey ? MODE_CENTER : MODE_HANDLE),
                        signX = dim === Y ? null : signsX[type],
                        signY = dim === X ? null : signsY[type],
                        state = local(that),
                        extent = state.extent,
                        selection = state.selection,
                        W = extent[0][0], w0, w1,
                        N = extent[0][1], n0, n1,
                        E = extent[1][0], e0, e1,
                        S = extent[1][1], s0, s1,
                        dx,
                        dy,
                        moving,
                        lockX,
                        lockY,
                        point0 = d3Selection.mouse(that),
                        point = point0,
                        emit = emitter(that, arguments).beforestart();

                    if (type === "overlay") {
                        state.selection = selection = [
                            [w0 = dim === Y ? W : point0[0], n0 = dim === X ? N : point0[1]],
                            [e0 = dim === Y ? E : w0, s0 = dim === X ? S : n0]
                        ];
                    } else {
                        w0 = selection[0][0];
                        n0 = selection[0][1];
                        e0 = selection[1][0];
                        s0 = selection[1][1];
                    }

                    w1 = w0;
                    n1 = n0;
                    e1 = e0;
                    s1 = s0;

                    var group = d3Selection.select(that)
                        .attr("pointer-events", "none");

                    var overlay = group.selectAll(".overlay")
                        .attr("cursor", cursors[type]);

                    if (d3Selection.event.touches) {
                        group
                            .on("touchmove.brush", moved, true)
                            .on("touchend.brush touchcancel.brush", ended, true);
                    } else {
                        var view = d3Selection.select(d3Selection.event.view)
                            .on("keydown.brush", keydowned, true)
                            .on("keyup.brush", keyupped, true)
                            .on("mousemove.brush", moved, true)
                            .on("mouseup.brush", ended, true);

                        d3Drag.dragDisable(d3Selection.event.view);
                    }

                    nopropagation();
                    d3Transition.interrupt(that);
                    redraw.call(that);
                    emit.start();

                    function moved() {
                        var point1 = d3Selection.mouse(that);
                        point = point1;
                        moving = true;
                        noevent();
                        move();
                    }

                    function move() {
                        var t;

                        dx = point[0] - point0[0];
                        dy = point[1] - point0[1];

                        switch (mode) {
                            case MODE_SPACE:
                            case MODE_DRAG: {
                                if (signX) dx = Math.max(W - w0, Math.min(E - e0, dx)), w1 = w0 + dx, e1 = e0 + dx;
                                if (signY) dy = Math.max(N - n0, Math.min(S - s0, dy)), n1 = n0 + dy, s1 = s0 + dy;
                                break;
                            }
                            case MODE_HANDLE: {
                                if (signX < 0) dx = Math.max(W - w0, Math.min(E - w0, dx)), w1 = w0 + dx, e1 = e0;
                                else if (signX > 0) dx = Math.max(W - e0, Math.min(E - e0, dx)), w1 = w0, e1 = e0 + dx;
                                if (signY < 0) dy = Math.max(N - n0, Math.min(S - n0, dy)), n1 = n0 + dy, s1 = s0;
                                else if (signY > 0) dy = Math.max(N - s0, Math.min(S - s0, dy)), n1 = n0, s1 = s0 + dy;
                                break;
                            }
                            case MODE_CENTER: {
                                if (signX) w1 = Math.max(W, Math.min(E, w0 - dx * signX)), e1 = Math.max(W, Math.min(E, e0 + dx * signX));
                                if (signY) n1 = Math.max(N, Math.min(S, n0 - dy * signY)), s1 = Math.max(N, Math.min(S, s0 + dy * signY));
                                break;
                            }
                        }

                        if (e1 < w1) {
                            signX *= -1;
                            t = w0, w0 = e0, e0 = t;
                            t = w1, w1 = e1, e1 = t;
                            if (type in flipX) overlay.attr("cursor", cursors[type = flipX[type]]);
                        }

                        if (s1 < n1) {
                            signY *= -1;
                            t = n0, n0 = s0, s0 = t;
                            t = n1, n1 = s1, s1 = t;
                            if (type in flipY) overlay.attr("cursor", cursors[type = flipY[type]]);
                        }

                        if (state.selection) selection = state.selection; // May be set by brush.move!
                        if (lockX) w1 = selection[0][0], e1 = selection[1][0];
                        if (lockY) n1 = selection[0][1], s1 = selection[1][1];

                        if (selection[0][0] !== w1
                            || selection[0][1] !== n1
                            || selection[1][0] !== e1
                            || selection[1][1] !== s1) {
                            state.selection = [[w1, n1], [e1, s1]];
                            redraw.call(that);
                            emit.brush();
                        }
                    }

                    function ended() {
                        nopropagation();
                        if (d3Selection.event.touches) {
                            if (d3Selection.event.touches.length) return;
                            if (touchending) clearTimeout(touchending);
                            touchending = setTimeout(function() { touchending = null; }, 500); // Ghost clicks are delayed!
                            group.on("touchmove.brush touchend.brush touchcancel.brush", null);
                        } else {
                            d3Drag.dragEnable(d3Selection.event.view, moving);
                            view.on("keydown.brush keyup.brush mousemove.brush mouseup.brush", null);
                        }
                        group.attr("pointer-events", "all");
                        overlay.attr("cursor", cursors.overlay);
                        if (state.selection) selection = state.selection; // May be set by brush.move (on start)!
                        if (empty(selection)) state.selection = null, redraw.call(that);
                        emit.end();
                    }

                    function keydowned() {
                        switch (d3Selection.event.keyCode) {
                            case 18: { // ALT
                                if (mode === MODE_HANDLE) {
                                    if (signX) e0 = e1 - dx * signX, w0 = w1 + dx * signX;
                                    if (signY) s0 = s1 - dy * signY, n0 = n1 + dy * signY;
                                    mode = MODE_CENTER;
                                    move();
                                }
                                break;
                            }
                            case 32: { // SPACE; takes priority over ALT
                                if (mode === MODE_HANDLE || mode === MODE_CENTER) {
                                    if (signX < 0) e0 = e1 - dx; else if (signX > 0) w0 = w1 - dx;
                                    if (signY < 0) s0 = s1 - dy; else if (signY > 0) n0 = n1 - dy;
                                    mode = MODE_SPACE;
                                    overlay.attr("cursor", cursors.selection);
                                    move();
                                }
                                break;
                            }
                            default: return;
                        }
                        noevent();
                    }

                    function keyupped() {
                        switch (d3Selection.event.keyCode) {
                            case 18: { // ALT
                                if (mode === MODE_CENTER) {
                                    if (signX < 0) e0 = e1; else if (signX > 0) w0 = w1;
                                    if (signY < 0) s0 = s1; else if (signY > 0) n0 = n1;
                                    mode = MODE_HANDLE;
                                    move();
                                }
                                break;
                            }
                            case 32: { // SPACE
                                if (mode === MODE_SPACE) {
                                    if (d3Selection.event.altKey) {
                                        if (signX) e0 = e1 - dx * signX, w0 = w1 + dx * signX;
                                        if (signY) s0 = s1 - dy * signY, n0 = n1 + dy * signY;
                                        mode = MODE_CENTER;
                                    } else {
                                        if (signX < 0) e0 = e1; else if (signX > 0) w0 = w1;
                                        if (signY < 0) s0 = s1; else if (signY > 0) n0 = n1;
                                        mode = MODE_HANDLE;
                                    }
                                    overlay.attr("cursor", cursors[type]);
                                    move();
                                }
                                break;
                            }
                            default: return;
                        }
                        noevent();
                    }
                }

                function initialize() {
                    var state = this.__brush || {selection: null};
                    state.extent = extent.apply(this, arguments);
                    state.dim = dim;
                    return state;
                }

                brush.extent = function(_) {
                    return arguments.length ? (extent = typeof _ === "function" ? _ : constant([[+_[0][0], +_[0][1]], [+_[1][0], +_[1][1]]]), brush) : extent;
                };

                brush.filter = function(_) {
                    return arguments.length ? (filter = typeof _ === "function" ? _ : constant(!!_), brush) : filter;
                };

                brush.handleSize = function(_) {
                    return arguments.length ? (handleSize = +_, brush) : handleSize;
                };

                brush.on = function() {
                    var value = listeners.on.apply(listeners, arguments);
                    return value === listeners ? brush : value;
                };

                return brush;
            }

            exports.brush = brush;
            exports.brushX = brushX;
            exports.brushY = brushY;
            exports.brushSelection = brushSelection;

            Object.defineProperty(exports, '__esModule', { value: true });

        })));