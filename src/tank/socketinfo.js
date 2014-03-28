(function($) {
	"use strict";

	var protocol = window.location.protocol,
        hostname = window.location.hostname,
		port = window.location.port ? '8081' : '8080',
		socketuri = protocol + '//' + hostname + ':' + port,
                allsocket = $('.socketall'),
		allsocketinfo = $('.socketall .socketinfo'),
		allsocketicon = $('.allicon'),
                friendsocket = $('.socketfriends'),
		friendinfo = $('.socketfriends .socketinfo'),
		friendicon = $('.friendsicon'),
		user = tiddlyweb.status.username,
		currentUserTag = '@' + user;

	function timestampToday() {
		var date = new Date(),
			year = date.getUTCFullYear() + '',
			month = date.getUTCMonth() + 1 + '',
			day = date.getUTCDate() + '';
		day = day.length == 1 ? '0' + day : day;
		month = month.length == 1 ? '0' + month : month;
		return year + month + day + '*';
	}

	if (allsocketinfo.length) {
		var allInfo = new Tiddlers(allsocketinfo,
			socketuri,
			'/search?q=modified:' + timestampToday(),
			['*'],
			{});
		if (allInfo.io) {
			allInfo.start();
		} else {
			allsocketinfo.find('dd.nilactivity').text(
					'No socket server. Click the icon to search.');
		}


		allsocket.on('click', function() {
			allsocketinfo.toggle();
			if (allsocketicon.hasClass('fa-bell')) {
				allsocketicon.removeClass('fa-bell');
				allsocketicon.addClass('fa-bell-o');
			};
		});

		allsocket.on('tiddlersUpdate', function() {
			allsocketicon.removeClass('fa-bell-o');
			allsocketicon.addClass('fa-bell');
		});
	}

	if (friendinfo.length) {
		var friendInfo = new Tiddlers(friendinfo,
			socketuri,
			'/search?q=tag:"' + encodeURIComponent(currentUserTag) + '"',
			['tags/' + currentUserTag],
			{});

		if (friendInfo.io) {
			friendInfo.start();
		} else {
			friendinfo.find('dd.nilactivity').text(
					'No socket server. Click the icon to search.');
		}

		friendsocket.on('click', function() {
			friendinfo.toggle();
			if (friendicon.hasClass('fa-smile-o')) {
				friendicon.removeClass('fa-smile-o');
				friendicon.addClass('fa-meh-o');
			};
		});

		friendsocket.on('tiddlersUpdate', function(ev, tiddler) {
			friendicon.removeClass('fa-meh-o');
			friendicon.addClass('fa-smile-o');
		});
	}

}(jQuery));

