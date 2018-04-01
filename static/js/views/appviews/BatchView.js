/* * * * * * * * * * * * * * * * * * * * * *
 *                                 *
 *  UserView class                        *
 *                                         *
 *  Handle admin settings                  *
 *                                         *
 * * * * * * * * * * * * * * * * * * * * * */

import Modal from '../../utils/Modal.js'
import View from '../../core/View.js'
import MultiSelect from '../../utils/MultiSelect.js'
import Controls from '../../components/elements/footbar/Controls'
import TrackPreview from '../../components/elements/footbar/TrackPreview'
import {JSONParsedGetRequest} from "../../utils/Utils";
import Track from "../../core/Track.js";

class BatchView extends View {

    constructor() {
        super();

        this.bufferTracks = [];

        this._createUI();
    }

    fetchLatestData(callback) {
        var that = this;
        JSONParsedGetRequest(
            'track/getBuffer/',
            function(response) {
                that.bufferTracks = new Array(response.RESULT.length);
                for(var i = response.RESULT.length; i--;)
                    that.bufferTracks[i] = new Track(response.RESULT[i]);
                that._fillBatchRoundOne();
                callback();
            }
        );
    }

//  --------------------------------  PRIVATE METHODS  --------------------------------  //


    /**
     * method : _createUI (private)
     * class  : UserView
     * desc   : Build UI elements
     **/
    _createUI() {

        this.ui = {
            header: {
                container: document.createElement("DIV"),
                title:     document.createElement("H1"),
                preNB:     document.createElement("SPAN"),
                NB:        document.createElement("SPAN"),
                separator: document.createElement("SPAN"),
                TTL:       document.createElement("SPAN"),
                postTTL:   document.createElement("SPAN")
            },
            list: {
                container: document.createElement("DIV"),
                ul:        document.createElement("UL")
            }
        };

        this.ui.header.container.className  = "mzk-batch-header";
        this.ui.list.container.className    = "mzk-batch-list";

        this.ui.header.preNB.innerHTML      = "Upload Batch Processing ( ";
        this.ui.header.NB.innerHTML         = "0";
        this.ui.header.separator.innerHTML  = " / ";
        this.ui.header.TTL.innerHTML        = "42";
        this.ui.header.postTTL.innerHTML    = " )";

        this.ui.header.title.appendChild(this.ui.header.preNB);
        this.ui.header.title.appendChild(this.ui.header.NB);
        this.ui.header.title.appendChild(this.ui.header.separator);
        this.ui.header.title.appendChild(this.ui.header.TTL);
        this.ui.header.title.appendChild(this.ui.header.postTTL);
        this.ui.header.container.appendChild(this.ui.header.title);

        this.ui.list.container.appendChild(this.ui.list.ul);

        this.container.classList.add("mzk-batchview");
        this.container.appendChild(this.ui.header.container);
        this.container.appendChild(this.ui.list.container);

        this._fillBatchRoundOne();

        this._eventListener();
    }


    _fillBatchRoundOne() {

        this.ui.header.NB.innerHTML         = "0";
        this.ui.header.TTL.innerHTML        = this.bufferTracks.length;

        let imgPath = '/static/img/controls/';
        let OKed = new MultiSelect();
        let KOed = new MultiSelect();

        for(let i = 0; i < this.bufferTracks.length; ++i) {
            let li      = document.createElement("LI");
            let content = document.createElement("DIV");
            let imgs    = document.createElement("DIV");
            let accept  = document.createElement("IMG");
            let refuse  = document.createElement("IMG");
            let tagbtn  = document.createElement("IMG");

            accept.dataset.batchType = 'A';
            refuse.dataset.batchType = 'R';
            tagbtn.dataset.batchType = 'T';
            accept.dataset.batchIx   = i;
            refuse.dataset.batchIx   = i;
            tagbtn.dataset.batchIx   = i;

            content.className = "mzk-batch-content";
            accept.src = imgPath + "accepted.svg";
            refuse.src = imgPath + "refused.svg";
            tagbtn.src = imgPath + "edit.svg";
            new TrackPreview(content, this.bufferTracks[i]);
            new Controls(content, [1, 1], this.bufferTracks[i]);

            imgs.appendChild(tagbtn);
            imgs.appendChild(accept);
            imgs.appendChild(refuse);
            li.appendChild(content);
            li.appendChild(imgs);

            this.ui.list.ul.appendChild(li);
        }

        let that = this;
        this.ui.list.ul.addEventListener('click', function(event) {

            let ix = event.target.dataset.batchIx;
            if(event.target.dataset.batchType == 'A') {
                event.target.src = imgPath + (OKed.add(ix, true) ? "accepted-true.svg" : "accepted.svg");
                KOed.remove(ix);
                event.target.nextSibling.src = imgPath + "refused.svg";
            } else if(event.target.dataset.batchType == 'R') {
                event.target.src = imgPath + (KOed.add(ix, true) ? "refused-true.svg" : "refused.svg");
                OKed.remove(ix);
                event.target.previousSibling.src = imgPath + "accepted.svg";
            } else if(event.target.dataset.batchType == 'T') {
                (new Modal("editTag", [that.bufferTracks[ix]])).open();
            }

            that.ui.header.NB.innerHTML = OKed.getSize() + KOed.getSize();
        });

    }


    /**
     * method : _eventListener (private)
     * class  : UserView
     * desc   : UserView event listeners
     **/
    _eventListener() {
    }
}

export default BatchView