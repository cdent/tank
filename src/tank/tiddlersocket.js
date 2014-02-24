/*jslint vars: true */
/*global jQuery, io */
var Tiddlers = (function($) {

    "use strict";

    var Tiddlers = function(el, socketuri, sourceuri, updater, options) {
        this.el = el.find('dl');
        this.source = sourceuri + ';sort=-modified;limit=5;sort=modified';
        this.updater = updater;

		var searchURI = sourceuri + ';sort=-modified',
			socketsearch = el.find('.socketsearch');
		socketsearch.attr('href', searchURI);

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
			return 10;
		},

        generateItem: function(tiddler) {
            var href = friendlyURI(tiddler.uri),
                tiddlerDate = dateString(tiddler.modified),
				tank = tiddler.bag;

            var link = $('<a>').attr({'href': href}).text(tiddler.title);

			var dd = $('<dd>').text('in ' + tank);
			var span = $('<span>').addClass('modified').attr('title',
					tiddlerDate).text(tiddler.modified).timeago();
			dd.prepend(span);

            var dt = $('<dt>').append(link);

            return {dt: dt, dd: dd};
        },

        updateUI: function(noTrigger) {
            var tiddler = this.queue.shift();
			var item = this.generateItem(tiddler);

			if (! noTrigger) {
				this.el.trigger('tiddlersUpdate', tiddler);
			}
			this.el.prepend(item.dd);
			this.el.prepend(item.dt);
			while (this.el.children().length > this.sizer()) {
				this.el.children().last().remove();
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
