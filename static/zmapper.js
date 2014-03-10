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
}

function getUpdate() {
   var oReq = new XMLHttpRequest();
   oReq.onload = reqListener;
   oReq.open("GET", window.location.pathname+".json", true);
   oReq.send();
}

$(document).ready(function() {
   window.updater = window.setInterval(getUpdate,5000);
});
