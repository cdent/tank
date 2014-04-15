(function($) {
	"use strict";

	var container = $('#twinner'),
		form = container.find('form'),
		currentTiddlerURI = $('link[rel=edit]').attr('href'),
		currentBag = currentTiddlerURI.split('/')[2],
		currentTiddler = currentTiddlerURI.split('/')[4],
		username = window.tiddlyweb.status.username;

	function displayMessage(message) {
		var messageArea = form.find('.message');
		messageArea.text(message);
		setTimeout(function() {
			messageArea.fadeOut();
		}, 10000);
	}

    // return true only once for every member, even if dupes
    function uniqueMember(member, index, members) {
        return (members.indexOf(member, index + 1) == -1);
    }

	function submitForm(ev) {
		var targetBag = encodeURIComponent(username),
			targetTiddlerURI = currentTiddlerURI.replace(currentBag, targetBag),
			redir = window.location.href.replace(currentBag, targetBag),
			etag = targetBag + '/' + currentTiddler + '/0:hello',
			data = {
				text: form.find('textarea[name=text]').val(),
				tags: form.find('input[name=tags]').val().split(/,\s*/),
				type: 'text/x-markdown'
			};
		ev.preventDefault();
		$.ajax({
			type: 'PUT',
			url: targetTiddlerURI,
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function() {window.location.href = redir},
		    statusCode: {
				412: function() { displayMessage('That would clobber') },
				409: function() { displayMessage('Data conflict') }
			}
		});
	}

	function activateForm() {
		var targetBag = encodeURIComponent(username),
			targetTiddlerURI = currentTiddlerURI.replace(currentBag, targetBag),
			tags = form.find('input[name=tags]'),
			text = form.find('textarea[name=text]');
		$.ajax({
			type: 'GET',
			url: targetTiddlerURI,
			dataType: 'json'
		}).done(function(data) {
			if (data.tags) {
                // de-dupe tags
                tags.val(tags.val().split(/,\s*/).concat(data.tags)
                    .filter(uniqueMember).sort());
			}
			if (data.text) {
				text.val(data.text);
			}
		}).always(function() {
			form.find('input').prop('disabled', false);
			text.prop('disabled', false);
			form.on('submit', submitForm);
		});
	}

	var activator = container.find('h3'),
		arrow = activator.find('i').first();

	activator.on('click', function() {
		form.toggle();
		arrow.toggleClass('fa-chevron-right fa-chevron-down');
		activateForm();
	});

}(jQuery));
