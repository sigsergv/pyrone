var Pyrone_file_formAllowUpload = false;

function Pyrone_file_checkUploadForm(url, form_id) {
	if (Pyrone_file_formAllowUpload) {
		Pyrone_file_formAllowUpload = false;
		return true;
	}
	var form = $('#'+form_id);

	var fnf = $('#fid-filename'),
		fdf = $('#fid-filedata');
	
	// forbid empty form submission
	if (fdf.val() == '') {
		var msg = tr('SELECT_FILE_TO_UPLOAD'),
			e = $('#error-filename');
		Pyrone_notify(e, msg);
		fdf.focus();
		return false;
	}

	Pyrone_file_formAllowUpload = true;
	form.submit();
	/* // disable because of issue #4 (https://github.com/sigsergv/pyrone/issues/4)
	$.ajax({
		url: url,
		type: 'POST',
		dataType: 'json',
		data: {
			filename: fnf.val()
		}
	}).done(function(obj) {
		// check for duplicates
		if (obj.exists) {
			var msg = tr('FILE_NAME_ALREADY_EXISTS_IN_THE_STORAGE'),
				e = $('#error-filename');
			Pyrone_notify(e, msg);
			fnf.focus();
		} else {
			// submit
			Pyrone_file_formAllowUpload = true;
			form.submit();
		}
	});

	return false;
	*/
};

function Pyrone_file_uploadFormFileSelected() {
	var ctf = $('#fid-content_type'), 
		fnf = $('#fid-filename'), 
		dltf = $('#fid-dltype'), 
		e = $('#fid-filedata');

	var filename = '';
	var res = /[\/\\]([^\/\\]+)$/.exec(e.val());
	if (res) {
		filename = res[1];
	} else {
		filename = e.val();
	}
	fnf.val(filename);
	// detect values for other fields

	var types = [ [ /\.JPEG$/i, 'image/jpeg' ], [ /\.JPG$/i, 'image/jpeg' ],
			[ /\.PNG$/i, 'image/png' ], [ /\.GIF$/i, 'image/gif' ] ];

	var content_type = '';
	$.each(types, function(ind, t) {
		if (t[0].exec(filename)) {
			content_type = t[1];
			return false;
		}
	});

	switch (content_type) {
	case 'image/jpeg':
	case 'image/png':
	case 'image/gif':
		dltf.val('auto');
		break;

	default:
		dltf.val('download');
	}

	if (content_type === '') {
		content_type = 'application/octet-stream';
	}
	
	fnf.focus();
};

function Pyrone_file_listDeleteSelected(table_id, url) {
	// find all checkboxes in the table
	var selected_uids = Pyrone_getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		return;
	}

	$.ajax({
		url: url,
		type: 'POST',
		dataType: 'json',
		data: {
			uids: selected_uids.join(',')
		}
	}).done(function(data){
		$.each(data.deleted, function(ind, id) {
			var el = $('tr[data-row-value="'+id+'"]');
			el.remove();
		});
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});	
};

function Pyrone_file_listDeleteSelectedReq(table_id, url) {
	var selected_uids = Pyrone_getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		Pyrone_createLinkNotifyBox('delete-selected-btn', tr('SELECT_ITEMS_FIRST'));
		return;
	}
	// ask confirmation
	Pyrone_createConfirmLink('delete-selected-btn', function() { Pyrone_file_listDeleteSelected(table_id, url); });
};

function Pyrone_settings_saveSettings(url) {
	var field_names = ['site_title', 'site_base_url', 'site_copyright', 'elements_on_page',
	              'admin_notifications_email', 'notifications_from_email', 'image_preview_width', 'google_analytics_id',
                  'timezone', 'ui_lang', 'site_search_widget_code',
	              'tw_consumer_key', 'tw_consumer_secret', 'social_twitter_share_link_via', 'ui_theme'];

	var bool_field_names = ['admin_notify_new_comments', 'admin_notify_new_user',
		'social_twitter_share_link', 'social_twitter_share_link_show_count',
		'social_gplusone']
	var params = {};
	
	$.each(field_names, function(ind, field_name) {
		var e = $('#fid-'+field_name);
		params[field_name] = e.val();
	});
	$.each(bool_field_names, function(ind, field_name) {
		var e = $('#fid-'+field_name);
		if (e.prop('checked')) {
			params[field_name] = true;
		}
	});
	$.ajax({
		url: url,
		type: 'POST',
		data: params,
		dataType: 'json',
	}).done(function(json) {
			if (json.errors) {
				var focus_el = false;
				$.each(field_names, function(ind, field_name) {
					var error_value = json.errors[field_name],
						error_el = $('#error-'+field_name);
					
					if (error_value) {
						if (!focus_el) {
							focus_el = $('#fid-'+field_name);
						};
						Pyrone_notify(error_el, error_value, false, -1);
					} else {
						Pyrone_unnotify(error_el);
					}
				});
				if (focus_el) {
					focus_el.focus();
				}
			} else {
				Pyrone_notify($('#eid-notify'), tr('SETTINGS_SAVED'), false, 20000);
			}
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});	
};

function Pyrone_settings_widgets_pagesSave(url) {
	var e = $('#fid-widget_pages_pages_spec'),
		widget_pages_pages_spec = e.val();
	
	var params = {
		widget_pages_pages_spec: widget_pages_pages_spec
	};
	
	$.ajax({
		url: url,
		type: 'POST',
		data: params,
		dataType: 'json'
	}).done(function(json) {
		if (json.errors) {
		} else {
			Pyrone_notify($('#eid-notify'), tr('SETTINGS_SAVED'), false, 20000);
		}
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});	
};

Pyrone_account_listDeleteSelected = Pyrone_file_listDeleteSelected;
Pyrone_backup_listDeleteSelected = Pyrone_file_listDeleteSelected;

function Pyrone_account_listDeleteSelectedReq(table_id, url) {
	var selected_uids = Pyrone_getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		Pyrone_createLinkNotifyBox('delete-selected-btn', tr('SELECT_ITEMS_FIRST'));
		return;
	}
	// ask confirmation
	Pyrone_createConfirmLink('delete-selected-btn', function() { Pyrone_file_listDeleteSelected(table_id, url);});
};

function Pyrone_account_changeEmailVerified(email_id, new_state/*true|false*/, url) {
	$.ajax({
		url: url,
		type: 'POST',
		data: {
			id: email_id,
			is_verified: new_state ? 'true' : 'false'
		}
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
};

function Pyrone_backup_listDeleteSelectedReq(table_id, url) {
	var selected_uids = Pyrone_getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		Pyrone_createLinkNotifyBox('delete-selected-btn', tr('SELECT_ITEMS_FIRST'));
		return;
	}
	// ask confirmation
	Pyrone_createConfirmLink('delete-selected-btn', function() { Pyrone_backup_listDeleteSelected(table_id, url);});
};

function Pyrone_backup_backupNow(url) {
	$('#eid-backup-progress').show();
	$.ajax({
		url: url,
		type: 'POST'
	}).done(function() {
		$('#eid-backup-progress').hide();
		location.reload(true);
	}).fail(function() {
		$('#eid-backup-progress').hide();
		alert(tr('AJAX_REQUEST_ERROR'));
	});
};

function Pyrone_backup_startRestore(url) {
	// display mask layer or something like
	
	$('#eid-progress').show();

	$.ajax({
		url: url,
		type: 'POST',
		dataType: 'json'
	}).done(function(json) {
		$('#eid-progress').hide();
		if (json.error) {
			$('#eid-error').text(json.error);
			// $('#eid-error').show().delay(5000).hide();
			return;
		}
		alert(tr('BACKUP_RESTORE_COMPLETE'));
		location.assign('/');
	}).fail(function(){
		$('#eid-progress').hide();
		alert(tr('AJAX_REQUEST_ERROR'));
	});
};

function Pyrone_backup_startRestoreReq(url, restore_link_id) {
	// ask confirmation
	Pyrone_createConfirmLink(restore_link_id, function() {Pyrone_backup_startRestore(url);});
};
