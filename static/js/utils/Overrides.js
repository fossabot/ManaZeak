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


(function track_event_listeners()
{
    let original_add = Element.prototype.addEventListener;
    let original_rem = Element.prototype.removeEventListener;

    let validate_options = function(a, b)
    {
        if(a == null || b == null)
            return true;
        //This returns false if and only if a and b have a common option which is different
        for(let i in a)
            if(b[i] != null && b[i] != a[i])
                return false;
        for(let i in b)
            if(a[i] != null && a[i] != b[i])
                return false;
        return true;
    };

    //This keeps track of the event listeners
    Element.prototype.addEventListener = function(type, fct, options)
    {
        //This makes testing options a lot easier
        if(typeof options == "boolean")
            options = {capture: options};

        let signature = {
            type: type,
            fct: fct,
            options: options
        };
        if(!this.__listenersList__)
            this.__listenersList__ = [signature];
        else
            this.__listenersList__.push(signature);

        console.log(original_add);
        original_add.call(this, type, fct, options);
    };

    //This function can be called with null as arguments to match all listeners
    Element.prototype.removeEventListener = function(type, fct, options)
    {
        if(this.__listenersList__ == null)
            return;

        if(typeof options == "boolean")
            options = {capture: options};

        let signature;
        for(let i = this.__listenersList__.length; i--;)
        {
            if(this.__listenersList__[i] == null)
                continue;

            signature = this.__listenersList__[i];
            if(type == null || type == signature.type)
                if(fct == null || fct == signature.fct)
                    if(validate_options(options, signature.options)) {
                        original_rem.call(this, signature.type, signature.fct, signature.options);
                        this.__listenersList__[i] = null;
                    }
        }
    };
}());


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
