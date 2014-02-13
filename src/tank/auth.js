(function($) {
	"use strict";

	function deleteToken(ev) {
		var parent = $(this).parent(),
			title = parent.find('span').first().text();
		$.ajax({
			uri: '/auth',
			type: 'delete',
			data: JSON.stringify({title: title}),
			success: function() { parent.remove() },
			error: displayError,
		});
	}

	function addDeleter(item) {
		var click = $('<a>').on('click', deleteToken),
			ex = $('<i>').attr('class', 'fa fa-times-circle');
		click.append(ex);
		item.append(click);
	}

	function updateList(data) {
		$('input').hide();
		var li = $('<li><span class="title">' + data.title
			+ '</span> <span class="desc">' + data.text + '</span> </li>');
		addDeleter(li);
		$('.tokens').append(li);
	}

	function displayError(xhr, status, err) {
		$('.error').text(status);
	}

	function makeToken(ev) {
		$('input').show();
		$('form[name=create]').on('submit', function(ev) {
			var desc = $('input[name=desc]').val(),
				csrf_token = $('input[name=csrf_token]').val();
			ev.preventDefault();
			$.ajax({
				type: 'post',
				url: '/auth',
				data: {desc: desc, csrf_token: csrf_token},
				dataType: 'json',
				success: updateList,
				error: displayError
			});
		});
	}

	var click = $('<a>').on('click', makeToken),
		plus = $('<i>').attr('class', 'fa fa-plus-circle'),
		header = $('main h1').first();

	click.append(plus);
	header.append(click);

	$('.tokens li').each(function(i) { addDeleter($(this)); });

}(jQuery));
