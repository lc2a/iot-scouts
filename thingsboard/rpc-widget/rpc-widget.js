var controlapi;
self.onInit = function() {
  controlapi = self.ctx.controlApi;
}

$("#sendMessage").click(function() {
   controlapi.sendOneWayCommand("echo",{'message':$("#message").val(), 'color': $("#color").val()}, 5000);
});

$("#lowLight").click(function() {
   controlapi.sendOneWayCommand("echo",{'message':"Brightness"}, 5000);
});

self.onDestroy = function() {
}
