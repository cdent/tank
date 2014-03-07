(function($){
	"use strict"

	$('form[name=logout]').on('submit', function(ev) {
		if (!confirm('Would you like to sign out?')) {
			ev.preventDefault();
		}
	});
})(jQuery);
