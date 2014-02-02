jQuery(document).ready(function() {
	console.log('being called');
	var recipe = window.location.pathname.replace(/^\/comps\//, ''),
		port = window.location.port,
		host = window.location.protocol
			+ "//"
			+ window.location.hostname
			+ ((port != '80' || port != '443') ? ':' + port : ''),
		workspace = 'recipes/' + recipe,
		tiddlers = '/recipes/' + recipe + '/tiddlers?fat=1';

	var setCustomFields = function() {
		config.defaultCustomFields = {
			'server.workspace': workspace,
			'server.type': 'tiddlyweb',
			'server.host': host,
			'server.content-type': 'text/x-tiddlywiki'
		};
	}

	var toTiddler = function(json, host) {
		var created = Date.convertFromYYYYMMDDHHMM(json.created);
		var modified = Date.convertFromYYYYMMDDHHMM(json.modified);
		var fields = json.fields;
		fields["server.type"] = 'tiddlyweb';
		fields["server.host"] = host;
		fields["server.bag"] = json.bag;
		fields["server.title"] = json.title;
		if(json.recipe) {
			fields["server.recipe"] = json.recipe;
		}
		if(json.type && json.type != "None") {
			fields["server.content-type"] = json.type;
		}
		fields["server.permissions"] = json.permissions.join(", ");
		fields["server.page.revision"] = json.revision;
		fields["server.workspace"] = "bags/" + json.bag;
		var tiddler = new Tiddler(json.title);
		tiddler.assign(tiddler.title, json.text, json.modifier, modified, json.tags,
			created, json.fields, json.creator);
		return tiddler;
	};

	var init = function() {
		readOnly = false;
		var pluginProblem = loadPlugins("bootstrapPlugin");
		store.notifyAll();
		invokeParamifier(params,"onstart");
		story.closeAllTiddlers();
		story.displayDefaultTiddlers();
		window.scrollTo(0,0);
		setCustomFields(); // again
		refreshAll();
		if(pluginProblem) {
			story.displayTiddler(null,"PluginManager");
			displayMessage(config.messages.customConfigError);
		}
	}

	var success = function(json) {
		store = new TiddlyWiki({config: config});
		story = new Story('tiddlerDisplay', 'tiddler');
		for (var i = 0; i < json.length; i++) {
			var title = json[i].title;
			if (title !== 'app' && title !== 'bootstrap') {
				tid = toTiddler(json[i], host);
				if (tid.tags.indexOf('systemConfig') !== -1 &&
					tid.tags.indexOf('systemConfigDisable') === -1) {
						tid.tags.push('bootstrapPlugin');
				}
				store.addTiddler(tid);
				store.notify(tid.title);
				story.refreshTiddler(tid.title, null, true);
			}
		}
		init();
		console.log('success done');
	};

	setCustomFields();

	ajaxReq({
		dataType: 'json',
		url: tiddlers,
		success: success,
		error: function() {
			jQuery('#contentWrapper').addClass('error')
				.text('Error while loading');
		}
	});
});
