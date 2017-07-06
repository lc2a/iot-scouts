self.onInit = function() {
  //self.onDataUpdated();
}

self.onDataUpdated = function() {
    var kuva = self.ctx.data[0].data[0][1];
    if(typeof kuva != "undefined")
    {
        var options = {  
    weekday: "long", year: "numeric", month: "short",  
    day: "numeric", hour: "2-digit", minute: "2-digit"  };  
        var localdate = new Date();
        var picdate = new Date(Number(self.ctx.data[0].data[0][0]));
        kuva = kuva.slice(2,-1);
        console.log("picdate:", picdate);
        element = document.getElementById("kuva");
        element.innerHTML = "<p style='font-size:11px;'>"+picdate.toLocaleTimeString('fi-FI', options)+"</p><img style='width:98%;' src='data:image/jpg;base64,"+kuva+"'>";
    }

}

self.onDestroy = function() {
}