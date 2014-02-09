(function($) {
	"use strict";

	var container = $('#compmaker'),
		form = container.find('form'),
		select = form.find('select[name="bag"]'),
		currentTiddlerURI = $('link[rel=edit]').attr('href'),
		currentBag = unescape(currentTiddlerURI.split('/')[2]);

	function displayMessage(message) {
		var messageArea = form.find('.message');
		messageArea.text(message);
		setTimeout(function() {
			messageArea.fadeOut();
		}, 10000);
	}

	function putRecipe(chosenBag, name, desc) {
		var user = tiddlyweb.status.username,
			recipe = {
				policy: {
					owner: user,
					manage: [user],
				},
				recipe: [
					[currentBag, ''],
					[chosenBag, '']
				],
				desc: desc
			},
			recipeURI = '/recipes/' + encodeURIComponent(name),
			redir = window.location.origin + '/comps/' + encodeURIComponent(name);
		$.ajax({
			url: recipeURI,
			type: 'put',
			contentType: 'application/json',
			data: JSON.stringify(recipe),
			success: function() { window.location.href = redir },
			error: function(xhr, status, err) {
				return displayMessage('Unable to save: ' + status);
			}
		});
	}

	function checkName(chosenBag, name, desc) {
		$.ajax({
			url: '/recipes/' + encodeURIComponent(name),
			type: 'get',
			success: function() {
				return displayMessage('That name is in use');
			},
			statusCode: {
				404: function() { putRecipe(chosenBag, name, desc); }
			}
		});
	}

	function submitForm(ev) {
		var chosenBag = select.val(),
			name = form.find('input[name=name]').val(),
			desc = form.find('input[name=desc]').val();
		ev.preventDefault();
		if (!chosenBag || !name) {
			return displayMessage('Name and target required');
		}
		checkName(chosenBag, name, desc);
	}

	function activateForm() {
		select.prop('disabled', false);
		form.find('input').prop('disabled', false);
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
			url: '/bags?select=policy:write;sort=name',
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
