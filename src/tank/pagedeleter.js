(function($) {
	"use strict";

	var deleter = $('.delete'),
		tiddlerURI = $('link[rel=edit]').attr('href'),
		title = tiddlerURI.split('/')[4],
		tank = tiddlerURI.split('/')[2],
		top = '/tanks/' + tank;

	title = decodeURIComponent(title);
	if (title === 'index') {
		top = '/dash';
	}

	function deleteTiddler() {
		deleter.removeClass('fa-trash-o').addClass('fa-cog').addClass('fa-spin');
		$.ajax({
			url: tiddlerURI,
			type: 'DELETE',
			success: function() {window.location.pathname = top;},
		});
	}

	deleter.on('click', function() {
		if (confirm('Are you sure you want to delete this page, "'
				+ title + '"? '
				+ 'There is no recovery mechanism.')) {
			return deleteTiddler();
		}
	});

	deleter.css('display', 'inherit');
		

}(jQuery));
