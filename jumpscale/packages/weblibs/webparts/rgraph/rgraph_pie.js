var pie = new RGraph.Pie('{{config.pieId}}', {{config.pieData}});

pie.Set('chart.title', '{{config.pieTitle}}');
//pie.Set('chart.labels', {{config.pieLegend});
pie.Set('chart.shadow', true);
pie.Set('chart.linewidth', 1);
pie.Set('chart.exploded', 3);
pie.Set('chart.key', {{config.pieLegend}});

pie.Draw();
