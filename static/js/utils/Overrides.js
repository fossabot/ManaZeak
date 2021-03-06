/* * * * * * * * * * * * * * * * * * * * * *
 *                                         *
 *  This file is for overriding vanilla JS *
 *                                         *
 * * * * * * * * * * * * * * * * * * * * * */

Event.prototype.stop = function() {
    let target = this.target;

    if(target.nodeName == 'LABEL')
        target = target.firstChild;

    if(target.nodeName == 'A') {
        console.log("Manazeak's default event stop was prevented because it was called on a <a> element.")
        return;
    } else if(target.nodeName == 'INPUT' && target.type == 'checkbox')
        return;

    this.stopPropagation();
    this.stopImmediatePropagation();
    this.preventDefault();
};


(function forceStop() {
    let addEvent = Element.prototype.addEventListener;
    Element.prototype.addEventListener = function(type, handler, options) {
        addEvent.call(this, type, function(event) {
            if (options !== true) {
                event.stop();
            }

            handler.apply(this, arguments);
        }, options);
    }
}());


//Disable default loading of dropped files
window.addEventListener("dragover",function(e){
    e = e || event;
    e.preventDefault();
},false);


window.addEventListener("drop",function(e){
    e = e || event;
    e.preventDefault();
},false);
