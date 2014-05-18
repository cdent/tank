(function($){
	"use strict"

	var tank = decodeURIComponent(window.location.pathname.split('/')[2]),
		linkIcon = 'fa fa-link fa-rotate-90';

	$('.transclusion').find('.wikilink').attr('href',
		function(index, attr) {
			var article = $(this).parents('.transclusion').first();
			var bag = article.data('bag');
			if (bag !== tank) {
				return '../' + encodeURIComponent(bag) + '/' + attr;
			}
			return attr;
		});

	$('.transclusion').each(function(index) {
		var title = $(this).data('title'),
			uri = $(this).data('uri'),
			i = $('<i>').addClass(linkIcon),
			link = $('<a>').attr('href', uri).addClass('transicon').append(i);
		$(this).prepend(link);
	});

	$('.wikicontent *[id]').each(function(index) {
		var id = $(this).attr('id'),
			link = $('<a>')
				.attr('href', '#' + id)
				.addClass('plink')
				.text('\u00B6');
		if (!$(this).attr('id').indexOf('fnref-') == 0) {
			$(this).prepend(link);
		}
	});

})(jQuery);
