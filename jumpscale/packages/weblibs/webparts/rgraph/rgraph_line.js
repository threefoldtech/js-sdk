var line = new RGraph.Line("{{config.lineId}}", {{config.lineData}});

line.Set('chart.title', '{{config.lineTitle}}');
line.Set('chart.linewidth', 2);
line.Set('chart.labels', {{config.lineHeaders}});
line.Set('chart.key', {{config.lineLegend}});
line.Set('chart.gutter.left', 90);
RGraph.Effects.Line.jQuery.Trace(line);
line.Draw();
