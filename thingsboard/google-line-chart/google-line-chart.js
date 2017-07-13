self.drawChart = function (data) {

    // Set chart options
    var options = {
        title: 'Google line chart widget',
        curveType: 'function',
        legend: { position: 'bottom' }
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));

    chart.draw(data, options);
}

self.onInit = function () {
    self.ready = false;
    google.charts.load('current', { 'packages': ['corechart'] });
    google.charts.setOnLoadCallback(self.drawChart2);

}

self.drawChart2 = function () {
    self.ready = true;
}


self.GoogleChartConvert = function () {

    var subs = self.ctx.subscriptions;
    var labels = ["time"];
    var values = {};
    console.log(subs);
    Object.keys(subs).forEach(function (key) {
        var datasources = subs[key].data;
        console.log(datasources.length);
        for (var ii = 0; ii < datasources.length; ii++) {
            var label = subs[key].data[ii].dataKey["label"];
            labels.push(label);
            var datapoints = subs[key].data[ii].data;
            //console.log(label);
            for (var i = 0; i < datapoints.length; i++) {

                //console.log(datapoints[i]);
                var time = datapoints[i][0];
                var value = datapoints[i][1];
                if (typeof values[time] == "undefined") {
                    values[time] = [value, null];
                }
                else {
                    values[time][1] = value;
                }

            }
        }
    });
    //console.log("values: ", values);
    //console.log("labels: ", labels);
    var googleArray = [labels];
    var temp = [];
    var key;
    for (key in values) {
        temp = values[key];
        temp.unshift(key);
        googleArray.push(temp);
        //console.log(value);
    }
    console.log(googleArray);

    return googleArray;
}



self.onDataUpdated = function () {

    var data = self.GoogleChartConvert();
    if (self.ready) {
        self.drawChart(google.visualization.arrayToDataTable(data));
    }

}