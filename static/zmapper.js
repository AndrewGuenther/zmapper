function setVal(prefix, prop, data) {
   var elem = document.getElementById(prefix + prop);

   if (elem == null) {
      return;
   }

   while (elem.firstChild) {
      elem.removeChild(elem.firstChild);
   }

   elem.appendChild(document.createTextNode(data[prop]));
}

function setVals(prefix, data) {
   for (prop in data) {
      if (typeof data[prop] == "object") {
         setVals(prefix + prop, data[prop]);
      } else {
         setVal(prefix, prop, data);
      }
   }
}

function reqListener() {
   data = JSON.parse(this.responseText);

   setVals("", data);
   if (data) {
      $("#overall-progress").css("width", data['progress']+"%");
   }
}

function getUpdate() {
   var oReq = new XMLHttpRequest();
   oReq.onload = reqListener;
   oReq.open("GET", "status", true);
   oReq.send();
}

$(document).ready(function() {
   $("#start").click(function() {
      $.ajax("start");
      window.updater = window.setInterval(getUpdate,5000);
      $(this).attr("disabled","disabled");
      $("#stop").removeAttr("disabled");
   });

   $("#stop").click(function() {
      $.ajax("stop");
      window.clearInterval(window.updater);
      $(this).attr("disabled","disabled");
      $("#start").removeAttr("disabled");
   });

   $.ajax("started").done(function(data) {
      if (data == "True") {
         $("#start").click();
      }
   });
});
