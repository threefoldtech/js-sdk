var bar = new RGraph.Bar('{{config.chartId}}', {{chartData}});

    bar.Set('chart.title', '{{config.chartTitle}}');
    bar.Set('chart.labels', '{{config.chartHeaders})';
    bar.Set('chart.key', '{{config.chartLegend}}');
    // Set gutter wide enough to allow (very) big numbers in the y-axis labels
    bar.Set('chart.gutter.left', 90);
    bar.Set('chart.events.click', {{config.onclickfunction}});

    bar.Draw();
