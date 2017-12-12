/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                                     *
 *  PlaylistPreview class - handle the playlist info container (right/footbar)         *
 *                                                                                     *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
let PlaylistPreview = function(container) {

    this.ui = {
        container:     document.createElement("DIV"),
        name:          document.createElement("LI"),
        total:         document.createElement("LI"),
        duration:      document.createElement("LI"),
        repeatShuffle: document.createElement("LI"),
        repeat:        document.createElement("SPAN"),
        genre:         document.createElement("SPAN"),
        shuffle:       document.createElement("SPAN")
    };

    this.tooltipWrapper = document.createElement("DIV");
    this.listContainer  = document.createElement("UL");

    this.tooltipWrapper.className = "tooltipWrapper";

    this.ui.container.id          = "playlistPreview";
    this.ui.name.id               = "playlistPreviewName";
    this.ui.total.id              = "playlistPreviewTotal";
    this.ui.duration.id           = "playlistPreviewDuration";
    this.ui.repeat.id             = "playlistPreviewRepeat";
    this.ui.shuffle.id            = "playlistPreviewShuffle";

    this.ui.repeatShuffle.appendChild(this.ui.repeat);
    this.ui.repeatShuffle.appendChild(this.ui.shuffle);

    this.listContainer.appendChild(this.ui.name);
    this.listContainer.appendChild(this.ui.total);
    this.listContainer.appendChild(this.ui.duration);
    this.listContainer.appendChild(this.ui.repeatShuffle);

    this.ui.container.appendChild(this.listContainer);
    this.ui.container.appendChild(this.tooltipWrapper);

    container.appendChild(this.ui.container);
};


PlaylistPreview.prototype = {

    changePlaylist: function(playlist) {
        this.ui.name.innerHTML     = playlist.name;
        this.ui.total.innerHTML    = playlist.trackTotal + " tracks";
        this.ui.duration.innerHTML = secondsToTimecode(playlist.durationTotal);

        this.updatePlaylistPreview();
    },


    updatePlaylistPreview: function() {
        // TODO : link to App.controler event
        let repeatMode = window.app.activePlaylist.getRepeatMode();
        let shuffleMode = window.app.activePlaylist.getshuffleMode();

        switch (repeatMode) {
            case 0:
                this.ui.repeat.innerHTML = "Repeat off";
                break;

            case 1:
                this.ui.repeat.innerHTML = "Repeat one";
                break;

            case 2:
                this.ui.repeat.innerHTML = "Repeat all";
                break;

            default:
                // TODO : Switch default event
                break;
        }

        switch (shuffleMode) {
            case 0:
                this.ui.shuffle.innerHTML = " - Shuffle off";
                break;

            case 1:
                this.ui.shuffle.innerHTML = " - Random";
                break;

            case 2:
                this.ui.shuffle.innerHTML = " - Shuffle on";
                break;

            default:
                // TODO : Switch default event
                break;
        }
    },


    setVisible: function(visible) {
        this.ui.container.style.opacity = visible ? 1 : 0;
    }
};