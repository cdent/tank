(function($) {
	"use strict";

	var handlers = makeHandlers();

	new Checklists("main", handlers.retriever, handlers.storer);

	function makeHandlers() {
		var cache = {};
		var cacher = function(callback) {
			return function(data, status, xhr) {
				cache.tiddler = data;
				cache.etag = xhr.getResponseHeader("Etag");
				callback.call(this, data.text);
			};
		}
		var retriever = function(checkbox, callback) {
			cache.uri = $("link[rel=edit]").attr("href");
			$.ajax({
				type: "get",
				url: cache.uri,
				dataType: "json",
				success: cacher(callback)
				// TODO: error handling
			});
		};
		var storer = function(markdown, checkbox, callback) {
			cache.tiddler.text = markdown;
			$.ajax({
				beforeSend: function(xhr, settings) {
					xhr.setRequestHeader("If-Match", cache.etag)
				},
				type: "put",
				url: cache.uri,
				data: JSON.stringify(cache.tiddler),
				contentType: "application/json",
				success: callback
				// TODO: error handling
			});
		};
		return { retriever: retriever, storer: storer };
	}
}(jQuery));
