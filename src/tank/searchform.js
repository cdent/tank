(function($) {
	"use strict";

	var form = $('form[name=search]'),
		query = $('form[name=search] input[name=q]'),
		globalizer = $('form[name=search] .globalizer'),
		input = globalizer.find('input'),
		tiddlerURI = $('link[rel=edit]').attr('href'),
		bag = tiddlerURI.split('/')[2];

	input.on('click', function(ev) {
		var state = $(this).prop('checked');
		if (state) {
			query.attr('placeholder', 'Search all of tank');
		} else {
			query.attr('placeholder', 'Search this tank');
		}
	});

	form.on('submit', function(ev) {
		var state = input.prop('checked'),
			queryVal = query.val();
		if (!state) {
			query.val(queryVal + ' bag:"' + bag + '"');
		}
	});

	globalizer.css('display', 'inherit');
		

}(jQuery));
