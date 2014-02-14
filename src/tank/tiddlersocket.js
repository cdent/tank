/*jslint vars: true */
/*global jQuery, io */
var Tiddlers = (function($) {

    "use strict";

    var Tiddlers = function(el, socketuri, sourceuri, updater, options) {
        this.el = el;
        this.source = sourceuri + ';sort=modified';
        this.updater = updater;
        if (typeof(io) !== 'undefined') {
            this.socket = io.connect(socketuri,
                    {'force new connection': true});
            var self = this;
            this.socket.on('connect', function() {
                $.each(self.updater, function(index, sub) {
                    self.socket.emit('unsubscribe', sub);
                    self.socket.emit('subscribe', sub);
                });
                self.socket.on('tiddler', function(data) {
                    self.getTiddler(data);
                });
            });
        }
    };

    $.extend(Tiddlers.prototype, {
        queue: [],

        start: function() {
            var self = this;
            $.ajax({
                dataType: 'json',
                url: this.source,
                success: function(tiddlers) {
                    $.each(tiddlers, function(index, tiddler) {
                        self.push(tiddler, true);
                    });
                }
            });
        },

        push: function(tiddler, noTrigger) {
            this.queue.push(tiddler);
            this.updateUI(noTrigger);
        },

		sizer: function() {
			return 5;
		},

        generateItem: function(tiddler) {
            var href = friendlyURI(tiddler.uri),
                tiddlerDate = dateString(tiddler.modified),
				tank = tiddler.bag;

            var link = $('<a>').attr({'href': href}).text(tiddler.title);

			var extra = $('<span>').text(' in ' + tank);

            // jquery data() plays funny when the element is not part of the DOM
            // so use attr()
            var li = $('<li>')
                .attr("data-tiddler-uri", tiddler.uri)
                .append(link)
				.append(extra);
            return li;
        },

        updateUI: function(noTrigger) {
            var tiddler = this.queue.shift();
			var li = this.generateItem(tiddler);

			if (! noTrigger) {
				this.el.trigger('tiddlersUpdate', tiddler);
			}
			this.el.prepend(li);
			while (this.el.children().length > this.sizer()) {
				this.el.children().last().remove();
			}
        },

        getTiddler: function(uri) {
            var self = this;
            $.ajax({
                dataType: 'json',
                url: uri,
                success: function(tiddler) {
                    self.push(tiddler);
                }
            });
        }

    });

    function friendlyURI(uri) {
		return uri.replace(/\/bags\//, '/tanks/')
			.replace(/tiddlers\//, '');
    }

    function dateString(date) {
        return new Date(Date.UTC(
            parseInt(date.substr(0, 4), 10),
            parseInt(date.substr(4, 2), 10) - 1,
            parseInt(date.substr(6, 2), 10),
            parseInt(date.substr(8, 2), 10),
            parseInt(date.substr(10, 2), 10),
            parseInt(date.substr(12, 2) || "0", 10),
            parseInt(date.substr(14, 3) || "0", 10)
            )).toISOString();
    }

    return Tiddlers;

}(jQuery));
