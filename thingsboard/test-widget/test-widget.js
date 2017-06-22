self.onInit = function() {
    console.log("HELLO");
}

self.onDataUpdated = function() {
    var subs = self.ctx.subscriptions;
    var divi = document.getElementById('testwidget');
    divi.innerHTML = "";
    console.log(subs);
    Object.keys(subs).forEach(function(key) {
        var datasources = subs[key].data;
        console.log(datasources.length);
        for (var ii = 0; ii < datasources.length; ii++) {
            var label = subs[key].data[ii].dataKey["label"];
            var datapoints = subs[key].data[ii].data;
            var sum = 0;
            console.log(label);
            for (var i = 0; i < datapoints.length; i++) {
                // Iterate over numeric indexes from 0 to 5, as everyone expects.
                //console.log(datapoints[i]);
                sum = sum + datapoints[i][1];
                
            }
            
            divi.innerHTML = divi.innerHTML + label + " avg: " + sum/datapoints.length+"<br>";

        }



    });


}

self.onResize = function() {

}

self.onEditModeChanged = function() {

}

self.onMobileModeChanged = function() {

}

self.getSettingsSchema = function() {

}

self.getDataKeySettingsSchema = function() {

}

self.onDestroy = function() {

}