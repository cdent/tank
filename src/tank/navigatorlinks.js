(function($) {
	"use strict";

	var place = $('.navigatorlinks'),
		next = $('link[rel=next]').attr('href'),
		prev = $('link[rel=prev]').attr('href');

	if (prev) {
		$('<a>').attr({href: prev, title: 'earlier'}).addClass('prev')
			.addClass('fa fa-chevron-left')
			.appendTo(place);
	}

	if (next) {
		$('<a>').attr({href: next, title: 'later'}).addClass('next')
			.addClass('fa fa-chevron-right')
			.appendTo(place);
	}

}(jQuery));
