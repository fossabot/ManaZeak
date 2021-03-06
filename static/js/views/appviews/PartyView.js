/* * * * * * * * * * * * * * * * * * * * * *
 *                                         *
 *  PartyView class                        *
 *                                         *
 *  Handle admin settings                  *
 *                                         *
 * * * * * * * * * * * * * * * * * * * * * */

import { JSONParsedPostRequest, secondsToDate } from '../../utils/Utils.js'
import Notification from '../../utils/Notification.js'
import Track from '../../core/Track.js'
import View from '../../core/View.js'
import Controls from '../../components/elements/footbar/Controls.js'
import Shortcut from '../../utils/Shortcut.js'

class PartyView extends View {

    constructor() {
        super();
        this._createUI();
        this._eventListener();
        this._startClock();
        new Controls(this.ui.coverContainer, false, false);
    }

//  --------------------------------  PUBLIC METHODS  ---------------------------------  //

    /**
     * method : _createUI (public)
     * class  : PartyView
     * desc   : Returns container while fetching details about current track in player
     **/
    getContainer() {
        let currentlyPlaying = window.app.player.getSourceID();
        if(currentlyPlaying != -1) {

            let that = this;
            JSONParsedPostRequest(
                "track/getDetailedInfo/",
                JSON.stringify({
                    TRACK_ID: [window.app.player.getSourceID()]
                }),
                function (response) {
                    /* response = {
                     *     DONE      : bool
                     *     ERROR_H1  : string
                     *     ERROR_MSG : string
                     *
                     *     RESULT    : {
                     *         ID:
                     *         TITLE:
                     *         YEAR:
                     *         COMPOSER:
                     *         PERFORMER:
                     *         TRACK_NUMBER:
                     *         BPM:
                     *         LYRICS:
                     *         COMMENT:
                     *         BITRATE:
                     *         SAMPLERATE:
                     *         DURATION:
                     *         GENRE:
                     *         FILE_TYPE:
                     *         DISC_NUMBER:
                     *         SIZE:
                     *         LAST_MODIFIED:
                     *         COVER:
                     *         ARTISTS: {
                     *            ID:
                     *            NAME:
                     *         }
                     *         ALBUM: {
                     *             ID:
                     *             TITLE:
                     *             TOTAL_DISC:
                     *             TOTAL_TRACK:
                     *             ARTISTS: {
                     *                 ID:
                     *                 NAME:
                     *             }
                     *         }
                     *         PLAY_COUNTER:
                     *         FILE_NAME:
                     *     }
                     * } */
                    if (response.DONE) {
                        that._setCurrentTrack(new Track(response.RESULT[0]));
                    }

                    else {
                        new Notification("ERROR", response.ERROR_H1, response.ERROR_MSG);
                    }
                }
            );
        }

        return this.ui.container;
    }

//  --------------------------------  PRIVATE METHODS  --------------------------------  //

    /**
     * method : _createUI (private)
     * class  : PartyView
     * desc   : Build UI elements
     **/
    _createUI() {
        this.ui = {
            container:              this.container,
            mzkLogo:                document.createElement("IMG"),

            sparksContainer:        document.createElement("DIV"),
            sparksLayer1:           document.createElement("DIV"),
            sparksLayer2:           document.createElement("DIV"),
            sparksLayer3:           document.createElement("DIV"),
            sparksLayer4:           document.createElement("DIV"),

            coverContainer:         document.createElement("DIV"),
            trackContainer:         document.createElement("DIV"),
            trackCover:             document.createElement("IMG"),

            trackInfoContainer:     document.createElement("DIV"),
            trackComposerContainer: document.createElement("DIV"),
            trackTitle:             document.createElement("H1"),
            trackArtist:            document.createElement("H2"),
            trackYearAlbum:         document.createElement("H2"),
            trackComposer:          document.createElement("H3"),
            trackComposerLabel:     document.createElement("H3"),
            trackGenre:             document.createElement("H3"),

            dateContainer:          document.createElement("DIV"),
            date:                   document.createElement("H3"),

            close:                  document.createElement("IMG"),
        };

        this.ui.container.classList.add("mzk-partyview");
        this.ui.mzkLogo.className            = "mzk-logo";
        // Smells like Grafikart here ;) (https://www.youtube.com/watch?v=rV6Xgb_4FFo)
        this.ui.sparksContainer.className    = "mzk-star";
        this.ui.sparksLayer1.className       = "mzk-start-layer";
        this.ui.sparksLayer2.className       = "mzk-start-layer";
        this.ui.sparksLayer3.className       = "mzk-start-layer";
        this.ui.sparksLayer4.className       = "mzk-start-layer";

        this.ui.coverContainer.className     = "mzk-party-cover-controls";
        this.ui.trackContainer.className     = "mzk-track-container";
        this.ui.mzkLogo.src                  = "/static/img/logo/manazeak.svg";
        this.ui.trackCover.src               = "/static/img/utils/defaultcover.svg";

        this.ui.trackInfoContainer.className = "mzk-party-track-info";
        this.ui.trackComposerContainer.className = "mzk-party-track-info-composers c";
        this.ui.trackTitle.className         = "a";
        this.ui.trackArtist.className        = "a";
        this.ui.trackYearAlbum.className     = "b";
        this.ui.trackGenre.className         = "d";

        this.ui.dateContainer.className      = "mzk-date";

        this.ui.close.className              = "mzk-close";
        this.ui.close.src                    = "/static/img/controls/left.svg";

        this.ui.sparksContainer.appendChild(this.ui.sparksLayer1);
        this.ui.sparksContainer.appendChild(this.ui.sparksLayer2);
        this.ui.sparksContainer.appendChild(this.ui.sparksLayer3);
        this.ui.sparksContainer.appendChild(this.ui.sparksLayer4);

        this.ui.trackComposerContainer.appendChild(this.ui.trackComposerLabel);
        this.ui.trackComposerContainer.appendChild(this.ui.trackComposer);

        this.ui.trackInfoContainer.appendChild(this.ui.trackTitle);
        this.ui.trackInfoContainer.appendChild(this.ui.trackArtist);
        this.ui.trackInfoContainer.appendChild(this.ui.trackYearAlbum);
        this.ui.trackInfoContainer.appendChild(this.ui.trackComposerContainer);
        this.ui.trackInfoContainer.appendChild(this.ui.trackGenre);

        this.ui.trackContainer.appendChild(this.ui.trackCover);
        this.ui.trackContainer.appendChild(this.ui.trackInfoContainer);
        this.ui.coverContainer.appendChild(this.ui.trackContainer);
        this.ui.dateContainer.appendChild(this.ui.date);

        this.ui.container.appendChild(this.ui.mzkLogo);
        this.ui.container.appendChild(this.ui.sparksContainer);
        this.ui.container.appendChild(this.ui.coverContainer);
        this.ui.container.appendChild(this.ui.dateContainer);
        this.ui.container.appendChild(this.ui.close);
    }


    /**
     * method : _eventListener (private)
     * class  : PartyView
     * desc   : PartyView event listeners
     **/
    _eventListener() {
        let that = this;
        this.ui.close.addEventListener("click", function() {
            window.app.restorePageContent();
        });

        window.app.listen("changeTrack", function(track) {
            that._setCurrentTrack(track);
        });

        window.app.listen("changeView", function(view) {
            if (view == that) {
                let el = document.body;

                let requestMethod = el.requestFullScreen || el.webkitRequestFullScreen
                    || el.mozRequestFullScreen || el.msRequestFullScreen;

                requestMethod.call(el);
            }

            else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }

                else if(document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                }

                else if(document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                }
            }
        });

        this.addShortcut(new Shortcut('keyup', 'Escape', function() {
            if(!that.container.classList.contains('mzk-view-hide'))
                window.app.restorePageContent();
        }));

    }


    /**
     * method : _setCurrentTrack (private)
     * class  : PartyView
     * desc   : Change current track in view
     **/
    _setCurrentTrack(track) {
        this.ui.trackCover.src           = track.cover;
        this.ui.trackTitle.innerHTML     = track.title;
        this.ui.trackArtist.innerHTML    = track.artist;
        this.ui.trackYearAlbum.innerHTML = track.album + "&nbsp;&nbsp;—&nbsp;&nbsp;" + track.year;

        this.ui.trackComposerLabel.innerHTML  = "Composed by:&nbsp;";
        this.ui.trackComposer.innerHTML  = this._setComposerString(track.composer);

        this.ui.trackGenre.innerHTML     = track.genre;
    }


    _setComposerString(composer) {
        return composer.replace(/;/g, "<br>");
    }


    _startClock() {
        let that = this;
        window.setInterval(function() {
            that._updateClock()
        }, 1000);
    }

    _updateClock() {
        this.ui.date.innerHTML = secondsToDate(new Date());
    }

//  ------------------------------  GETTERS / SETTERS  --------------------------------  //

}

export default PartyView