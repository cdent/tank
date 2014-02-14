(function($) {
	"use strict";

	var protocol = window.location.protocol,
        hostname = window.location.hostname,
		port = window.location.port ? '8081' : '8080',
		socketuri = protocol + '//' + hostname + ':' + port,
		allsocketinfo = $('.socketall .socketinfo'),
		allsocketicon = $('.socketall'),
		friendinfo = $('.socketfriends .socketinfo'),
		friendicon = $('.socketfriends'),
		user = tiddlyweb.status.username,
		currentUserTag = '@' + user;


	if (allsocketinfo.length) {
		var allInfo = new Tiddlers(allsocketinfo,
			socketuri,
			'/search?q=',
			['*'],
			{});
		allInfo.start();

		allsocketicon.on('click', function() {
			allsocketinfo.toggle();
			if (allsocketicon.hasClass('fa-bell')) {
				allsocketicon.removeClass('fa-bell');
				allsocketicon.addClass('fa-bell-o');
			};
		});

		allsocketicon.on('tiddlersUpdate', function() {
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
		friendInfo.start();

		friendicon.on('click', function() {
			friendinfo.toggle();
			if (friendicon.hasClass('fa-smile-o')) {
				friendicon.removeClass('fa-smile-o');
				friendicon.addClass('fa-meh-o');
			};
		});

		friendicon.on('tiddlersUpdate', function(ev, tiddler) {
			friendicon.removeClass('fa-meh-o');
			friendicon.addClass('fa-smile-o');
		});
	}

}(jQuery));

