from Jumpscale import j
import os

mypath = j.sal.fs.getDirName(os.path.abspath(__file__))


def _lib_add(self):
    self.jquery_add()
    self.js_add("%s/old/rgraph/RGraph.common.core.js" % self.liblocation)
    self.js_add("%s/old/rgraph/RGraph.bar.js" % self.liblocation)
    self.js_add("%s/old/rgraph/RGraph.pie.js" % self.liblocation)
    self.js_add("%s/old/rgraph/RGraph.line.js" % self.liblocation)
    self.js_add("%s/old/rgraph/RGraph.common.key.js" % self.liblocation)
    self.js_add("%s/old/rgraph/RGraph.common.effects.js" % self.liblocation)
    self.js_add("%s/old/rgraph/RGraph.common.dynamic.js" % self.liblocation)


def barchart_add(
    self, title, rows, headers="", width=900, height=400, showcolumns=[], columnAliases={}, onclickfunction=""
):
    """
    order is list of items in rows & headers, defines the order and which columns to show
    """

    self._lib_add()

    data = list()
    legend = list()
    newRows = []
    for row in rows:
        if len(row) < 2:
            continue
        newRow = [row[0]] + [int(n) for n in row[1:]]
        newRows.append(newRow)
    rows = newRows

    if len(rows) == 0:
        return False

    if showcolumns != []:
        rows2 = rows
        rows = []
        for row in rows2:
            if row[0] in showcolumns:
                rows.append(row)

    data = [list(x) for x in zip(*rows)][1:]

    for row in rows:
        if row[0] in columnAliases:
            legend.append(columnAliases[row[0]])
        else:
            legend.append(row[0])

    if str(headers) != "":
        if len(headers) == len(data) + 1:
            headers = headers[1:]
        # headers=[""]+headers
        if len(headers) != len(data):
            # raise RuntimeError("headers has more items then nr columns")
            print("Cannot process headers, wrong nr of cols")
            self.part_add("ERROR header wrong nr of cols:%s" % headers)
            headers = []

            # headers = [] #Wrong number of headers
    else:
        headers = []

    self._chartId += 1
    chartId = "chart-%s" % (self._chartId)

    config = {}
    config["chartId"] = chartId
    config["chartTitle"] = title
    config["chartData"] = data
    config["chartHeaders"] = headers
    config["chartLegend"] = legend
    config["chartWidth"] = width
    config["chartHeight"] = height

    if onclickfunction == "":
        onclickfunction = "function(){}"
        config["onclickfunction"] = onclickfunction

    # call the template engine
    jsContent = j.tools.jinja2.file_render("rgraph_bar.js", config)

    self.addScriptBodyJS(jsContent)
    chartContainer = "<canvas id='%s' width='%s' height='%s' >[No Canvas Support!]</canvas>" % (chartId, width, height)
    self.part_add(chartContainer, isElement=True, newline=True)


def piechart_add(self, title, data, legend, width=1000, height=600):
    """
    Add pie chart as the HTML element
    @param data is array of data points
    @param legend [legendDataPoint1, legendDataPoint2, ..]
    """
    self._lib_add()
    self._addChartJS()
    self._pieId += 1
    pieId = "pie-%s" % (self._pieId)

    # SEE BARCHART NEED TO BE DONE #TODO:*1
    te = j.tools.code.templateengine.new()
    te.add("pieId", pieId)
    te.add("pieTitle", title)
    te.add("pieData", str(data))
    te.add("pieLegend", str(legend))

    jsContent = te.replace(self._pieTemplateContent)

    self.addScriptBodyJS(jsContent)
    pieContainer = "<canvas id='%s' width='%s' height='%s' >[No Canvas Support!]</canvas>" % (pieId, width, height)
    self.part_add(pieContainer, isElement=True, newline=True)


def linechart_add(self, title, rows, headers="", width=800, height=400):
    """
    @param rows [[values, ...],]  first value of the row is the rowname e.g. cost, revenue
    @param headers [] first value is name of the different rowtypes e.g. P&L
    """
    self._lib_add()
    legend = list()

    headers2 = []
    prev = ""
    for item in headers:
        if item != prev:
            headers2.append(item)
            prev = item
        else:
            headers2.append("")

    if len(rows) == 0:
        return False
    data = ""
    for row in rows:
        data += str(row[1:]) + ","
        legend.append(row[0])

    data = data[:-1]

    self._addChartJS()
    self._lineId += 1
    lineId = "line-%s" % (self._lineId)

    if headers == "":
        headers = []

    te = j.tools.code.templateengine.new()
    te.add("lineId", lineId)
    te.add("lineTitle", title)
    te.add("lineData", data)
    te.add("lineHeaders", str(headers2))
    te.add("lineLegend", str(legend))
    te.add("lineWidth", str(width))
    te.add("lineHeight", str(height))

    # TODO:*1 like in barchart, read template and fill in

    lineContainer = "<canvas id='%s' width='%s' height='%s' >[No Canvas Support!]</canvas>" % (lineId, width, height)
    self.part_add(lineContainer, isElement=True, newline=True)

    self.js_add(jsContent=jsContent, header=False)
