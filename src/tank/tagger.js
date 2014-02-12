(function($) {
	"use strict";

	var selectizer,
		tags = [];

	function start() {
		if (selectizer) {
			selectizer.destroy();
			tags = [];
		}
		var select = $('input[name=tags]').selectize({
			delimeter: ',',
			create: true,
			preload: true,
			load: function(query, callback) {
				getTags(callback);
			}
		});
		selectizer = select[0].selectize;
	}

	function getTags(callback) {
		if (tags.length > 0) {
			return callback(tags);
		}
		var uri = '/tags',
			query = window.location.search.replace(/^.*bag=([^;]*);.*$/, '$1');
		if (! $('input[name=global]').is(':checked')) {
			uri = uri + '?q=bag:' + query;
		}
		$.ajax({
			type: 'get',
			url: uri,
			success: function(data) {
				$.each(data.split(/\n/), function(index, item) {
					if (item) {
						tags.push({value: item, text: item});
					}
				});
				return callback(tags);
			}
		});
	}

	$('input[name=global]').on('click', function(ev) {
		start();
	});
	start();

}(jQuery));
