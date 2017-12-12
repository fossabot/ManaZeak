/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                                     *
 *  ProgressBar class - handle the progress bar depending on current track             *
 *                                                                                     *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
let ProgressBar = function(container) {

    this._createUI(container);

    this._init();
};


ProgressBar.prototype = {

    _init: function () {
        this.moodbar.container = document.getElementById("moodbar");
        this.moodbar.thumb     = document.getElementById("moodbarThumb");

        this.duration.current.innerHTML = "--:--";
        this.duration.total.innerHTML   = "--:--";

        this._eventListener();
    },


    _createUI: function(container) {
        this.container = document.createElement("DIV");
        this.progressBar = {
            container:   document.createElement("DIV"),
            current:     document.createElement("DIV"),
            thumb:       document.createElement("DIV")
        };
        this.duration = {
            current:     document.createElement("SPAN"),
            total:       document.createElement("SPAN"),
            hover:       document.createElement("DIV")
        };

        this.container.id             = "progressBarWrapper";

        this.progressBar.container.id = "progressBar";
        this.progressBar.current.id   = "progress";
        this.progressBar.thumb.id     = "progressThumb";

        this.duration.current.id      = "currentDuration";
        this.duration.total.id        = "totalDuration";
        this.duration.hover.id        = "progressTimecodeHover";

        this.moodbar = {
            container: null,
            thumb:     null
        };

        this.refreshIntervalId = -1;

        this.isDragging  = false;
        this.isMouseOver = false;
        this.isInverted  = false;

        this.progressBar.container.appendChild(this.progressBar.current);
        this.progressBar.container.appendChild(this.progressBar.thumb);
        this.progressBar.container.appendChild(this.duration.hover);

        this.container.appendChild(this.duration.current);
        this.container.appendChild(this.progressBar.container);
        this.container.appendChild(this.duration.total);

        container.appendChild(this.container);
    },


    moveProgress: function (event, track) {
        let boundRect = 0;

        if (this.isDraggingOnMoodbar) {
            boundRect = this.moodbar.container.getBoundingClientRect();
        } else {
            boundRect = this.progressBar.container.getBoundingClientRect();
        }

        if (this.isDragging) {
            let distanceToLeftInPx = event.clientX - boundRect.left;
            let distanceToLeftInPr = (distanceToLeftInPx * 100) / boundRect.width;
            // OOB protection
            if (distanceToLeftInPr > 100) { distanceToLeftInPr = 100; }
            if (distanceToLeftInPr < 0)   { distanceToLeftInPr = 0;   }
            // Style assignation
            this.progressBar.current.style.width    = distanceToLeftInPr + "%";
            this.progressBar.thumb.style.marginLeft = distanceToLeftInPr + "%";
            this.moodbar.thumb.style.marginLeft     = distanceToLeftInPr + "%";
            // Changing track currentTime
            track.currentTime = (track.duration * distanceToLeftInPr) / 100;
            // Updating progress player -- /!\ Code under this while be trigger every sec due to setInterval() in init();
            this.updateProgress(track);
        }
    },


    updateProgress: function (track) {
        let distanceToLeftBorder = (track.currentTime * 100) / track.duration;
        // Style assignation
        this.progressBar.current.style.width    = distanceToLeftBorder + "%";
        this.progressBar.thumb.style.marginLeft = distanceToLeftBorder + "%";
        this.moodbar.thumb.style.marginLeft     = distanceToLeftBorder + "%";

        if (!this.isInverted) {
            this.duration.current.innerHTML = secondsToTimecode(track.currentTime);
            this.duration.total.innerHTML   = secondsToTimecode(track.duration);
        }

        else {
            this.duration.current.innerHTML = secondsToTimecode(track.currentTime);
            this.duration.total.innerHTML   = "-" + secondsToTimecode(track.duration - track.currentTime);
        }
    },


    timecodeProgressHover: function (event, track) {
        let boundRect = this.progressBar.container.getBoundingClientRect();
        let distanceToLeftInPx = event.clientX - boundRect.left;
        let distanceToLeftInPr = (distanceToLeftInPx * 100) / boundRect.width;
        // Avoid OOB
        if (distanceToLeftInPr > 100) { distanceToLeftInPr = 100; }
        if (distanceToLeftInPr < 0)   { distanceToLeftInPr = 0;   }

        let hoveredTimecode = secondsToTimecode((track.duration * distanceToLeftInPr) / 100);
        // We must convert back InPr to InPx ( distInPx = (boundRect.width * distanceToLeftInPr / 100) ) bc pixel size must be capped to progressBar bounds
        this.duration.hover.style.left = ((((boundRect.width * distanceToLeftInPr) / 100) - 30) * 100) / boundRect.width + "%";
        this.duration.hover.innerHTML  = hoveredTimecode;
    },


    refreshInterval: function (track) {
        let that = this;

        this.stopRefreshInterval();
        this.refreshIntervalId = window.setInterval(function () {
            that.updateProgress(track);
        }, 50); // Firing an updateProgress every 50ms to appear smooth on moodBar
    },


    stopRefreshInterval: function () {
        window.clearInterval(this.refreshIntervalId);
        this.refreshIntervalId = null;
    },


    invertTimecode: function () {
        this.isInverted = !this.isInverted;
    },


    resetProgressBar: function () {
        this.duration.current.innerHTML = "--:--";
        this.duration.total.innerHTML   = "--:--";
        this.duration.hover.innerHTML   = "--:--";

        this.progressBar.current.style.width    = 0 + "%";
        this.progressBar.thumb.style.marginLeft = 0 + "%";

        if (this.moodbar.thumb) {
            this.moodbar.thumb.style.marginLeft = 0 + "%";
        }

        this.stopRefreshInterval();
    },


    mouseMove: function (event) {
        if (this.isDragging) { // Updating the ProgressBar while user is moving the mouse
            this.moveProgress(event, window.app.player.getPlayer());
            addVisibilityLock(this.duration.hover);
            this.timecodeProgressHover(event, window.app.player.getPlayer());
        }

        else if (this.isMouseOver) {
            this.timecodeProgressHover(event, window.app.player.getPlayer());
        }
    },


    mouseDown: function (event) {
        //TODO: Clean this shit up
        if (!this.isDragging && (event.target.id === "progress" || event.target.id === "progressBar" || event.target.id === "progressThumb")) {
            this.isDragging          = true;

            this.stopRefreshInterval();
            this.moveProgress(event, window.app.player.getPlayer());
            window.app.mute();
        }

        else if (!this.isDragging && (event.target.id === "moodbar" || event.target.tagName === "rect" || event.target.id === "moodbarThumb")) {
            this.isDragging          = true;
            this.isDraggingOnMoodbar = true;

            this.stopRefreshInterval();
            this.moveProgress(event, window.app.player.getPlayer());
            window.app.mute();
        }
    },


    mouseUp: function () {
        if (this.isDragging) { // User released the ProgressBar thumb
            this.isDragging          = false;
            this.isDraggingOnMoodbar = false;

            this.refreshInterval(window.app.player.getPlayer());
            removeVisibilityLock(this.duration.hover);
            window.app.unmute();
        }
    },


    _eventListener: function () {
        let that = this;

        this.progressBar.container.addEventListener("mouseover", function () { that.isMouseOver = true; });
        this.progressBar.container.addEventListener("mouseleave", function () { that.isMouseOver = false; });
        this.duration.current.addEventListener("click", this.invertTimecode.bind(this));
        this.duration.total.addEventListener("click", this.invertTimecode.bind(this));

        window.addEventListener("mousemove", this.mouseMove.bind(this));
        window.addEventListener("mouseup", this.mouseUp.bind(this));
        window.addEventListener("mousedown", this.mouseDown.bind(this));
    }
};