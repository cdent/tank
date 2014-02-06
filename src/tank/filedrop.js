$(function() {

    var tank = window.location.pathname.replace(/^\/tanks\//, '').split('/')[0],
		dropzone = $('#dropzone');


    function dragNoop(ev) {
        ev.stopPropagation();
        ev.preventDefault();
    }

    function handleFile(file) {
        dropzone.text('Processing ' + file.name);

        var reader = new FileReader();
        reader.onerror = function(ev) {
			dropzone.text('Error ' + ev);
            console.log('error', ev);
        }
        reader.onload = function(ev) {
            var data = ev.target.result.replace(/^data[^,]*,/, '');
            var tiddler = {
                tags: [],
                text: data,
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
						dropzone.text('Processing ' + file.name + ' '
							+ Math.floor(evt.loaded/evt.total*100) + '%');
					};
					// return the customized object
					return xhr;
				},
				contentType: 'application/json',
				type: 'PUT',
				data: JSON.stringify(tiddler),
				processData: false,
				success: function() {
					dropzone.text('Uploaded ' + file.name);
				},
				error: function(xhr, status, error) {
					dropzone.text('Failed: ' + xhr.status + ' ' + error);
				}
			});
        }

        reader.onloadend = function(ev) {
            console.log('onloadend');
        }

        reader.readAsDataURL(file);
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
