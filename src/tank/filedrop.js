$(function() {

    var tank = window.location.pathname.replace(/^\/tanks\//, '').split('/')[0],
		dropzone = $('#dropzone'),
		dropzoneMessage = dropzone,
		injectText = false;

	if (!tank) {
		tank = window.location.search.replace(/^.*bag=([^;&]*)[;&].*$/, '$1');
		dropzoneMessage = $('#dropzoneMessage');
		injectText = true;
	}

    function dragNoop(ev) {
        ev.stopPropagation();
        ev.preventDefault();
    }

    function handleFile(file) {
        dropzoneMessage.text('Processing ' + file.name);

        var reader = new FileReader();
        reader.onerror = function(ev) {
			dropzoneMessage.text('Error ' + ev);
            console.log('error', ev);
        }
        reader.onloadend = function(ev) {
            var tiddler = {
                title: file.name,
                type: file.type,
            };
			$.ajax({
				url: '/bags/' + encodeURIComponent(tank) + '/tiddlers/'
					+ encodeURIComponent(tiddler.title),
				xhr: function() {
					// get the native XmlHttpRequest object
					var xhr = $.ajaxSettings.xhr();
					// set the onprogress event handler
					xhr.upload.onprogress = function(evt) {
						dropzoneMessage.text('Processing ' + file.name + ' '
							+ Math.floor(evt.loaded/evt.total*100) + '%');
					};
					// return the customized object
					return xhr;
				},
				contentType: file.type,
				type: 'PUT',
				data: reader.result,
				processData: false,
				success: function() {
					dropzoneMessage.text('Uploaded ' + file.name);
					if (injectText) {
						var cursorPosition = dropzone.prop('selectionEnd'),
							textAreaTxt = dropzone.val();
							txtToAdd = makeMarkdownLink(tiddler);
						dropzone.val(textAreaTxt.substring(0, cursorPosition)
								+ txtToAdd
								+ textAreaTxt.substring(cursorPosition) );
					}
				},
				error: function(xhr, status, error) {
					dropzoneMessage.text('Failed: ' + xhr.status + ' ' + error);
				}
			});
        }

        reader.readAsArrayBuffer(file);
    }

	function makeMarkdownLink(tiddler) {
		if (tiddler.type.match(/^image\//)) {
			return '![' + tiddler.title + ']('
				+ encodeURIComponent(tiddler.title) + ')\n';
		} else {
			return '[' + tiddler.title + ']('
				+ encodeURIComponent(tiddler.title) + ')\n';
		}
	}

    function dragDrop(ev) {
        ev.stopPropagation();
        ev.preventDefault();

        var files = ev.originalEvent.dataTransfer.files;
        var count = files.length;
        $.each(files, function(index, file) {
            handleFile(file);
        });
    }

    // init event handlers
    dropzone.on("dragenter", dragNoop);
    dropzone.on("dragexit", dragNoop);
    dropzone.on("dragover", dragNoop);
    dropzone.on("drop", dragDrop);
});
