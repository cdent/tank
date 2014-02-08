(function($) {
	"use strict";

	var container = $('#mover'),
		form = container.find('form'),
		select = form.find('select[name="bag"]'),
		currentTiddlerURI = $('link[rel=edit]').attr('href'),
		currentBag = currentTiddlerURI.split('/')[2],
		currentTiddler = currentTiddlerURI.split('/')[4];

	function displayMessage(message) {
		var messageArea = form.find('.message');
		messageArea.text(message);
		setTimeout(function() {
			messageArea.fadeOut();
		}, 10000);
	}

	function getChronicle(uri) {
		uri = uri + '/revisions?fat=1';
		return $.ajax({
			type: 'get',
			url: uri,
			dataType: 'json',
			processData: false
		});
	}

	function deleteTiddler(uri, redir) {
		$.ajax({
			type: 'delete',
			url: uri,
			success: function() { window.location.href = redir }
		});
	}

	function putChronicle(uri, originaluri, etag, redir, data) {
		return $.ajax({
			beforeSend: function(xhr, settings) {
				xhr.setRequestHeader('If-Match', etag)
			},
			type: 'post',
			url: uri + '/revisions',
			data: JSON.stringify(data),
			contentType: 'application/json',
			success: function() {deleteTiddler(originaluri, redir)},
		    statusCode: {
				412: function() { displayMessage('That would clobber') },
				409: function() { displayMessage('Data conflict') }
			}
		})
	}

	function submitForm(ev) {
		var chosenBag = encodeURIComponent(select.val()),
			targetTiddlerURI = currentTiddlerURI.replace(currentBag, chosenBag),
			redir = window.location.href.replace(currentBag, chosenBag),
			etag = chosenBag + '/' + currentTiddler + '/0:hello';
		console.log(chosenBag, redir);
		ev.preventDefault();
		$.when(getChronicle(currentTiddlerURI))
			.done(function(data) {
				return putChronicle(targetTiddlerURI, currentTiddlerURI,
					etag, redir, data);
			});
	}

	function activateForm() {
		select.prop('disabled', false);
		form.find('input[name="confirm"]').prop('disabled', false);
		form.on('submit', submitForm);
	}

	function processBags(data) {
		$.each(data, function(index, bag) {
			if (!bag.match(/^_/)) {
				var option = $('<option>').val(bag).text(bag);
				select.append(option);
			}
		});
		activateForm()
	}

	function loadBags() {
		$.ajax({
			type: 'get',
			url: '/bags?select=policy:create;sort=name',
			dataType: 'json',
			success: processBags
		});
	}

	var activator = container.find('h3'),
		arrow = activator.find('i').first();
	activator.one('click', function() {
		form.css('display', 'block');
		arrow.removeClass('fa-chevron-right').addClass('fa-chevron-down');
		loadBags();
	});

}(jQuery));
