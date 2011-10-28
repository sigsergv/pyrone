Ext.ns('Pyrone.file');
Ext.ns('Pyrone.backup');
Ext.ns('Pyrone.account');
Ext.ns('Pyrone.settings');
Ext.ns('Pyrone.settings.widgets');

Pyrone.file.formAllowUpload = false;

Pyrone.file.checkUploadForm = function(url, form_id) {
	var form = $e(form_id);
	if (Pyrone.file.formAllowUpload) {
		return true;
	}

	var fnf = $e('fid-filename'),
		fdf = $e('fid-filedata');
	
	// forbid empty form submission
	if (fdf && fdf.getValue() == '') {
		var x = _('aaa');
		var msg = tr('SELECT_FILE_TO_UPLOAD'),
			e = $e('error-filename');
		Pyrone.notify(e, msg);
		fdf.focus();
		return false;
	}
	
	// first check for duplicates
	Ext.Ajax.request({
		method: 'POST',
		url: url,
		params: {
			filename: fnf.getValue()
		},
		success: function(response, opts) {
			var obj = Ext.decode(response.responseText);
			if (obj.exists) {
				var msg = tr('FILE_NAME_ALREADY_EXISTS_IN_THE_STORAGE'),
					e = $e('error-filename');
				Pyrone.notify(e, msg);
				fnf.focus();
			} else {
				// submit
				Pyrone.file.formAllowUpload = true;
				form.dom.submit();
			}
		}
	});

	return false;
};

Pyrone.file.uploadFormFileSelected = function() {
	var ctf = $e('fid-content_type'), fnf = $e('fid-filename'), dltf = $e('fid-dltype'), e = $e('fid-filedata');

	function sct(v) {
		ctf.set({
			value: v
		});
	}

	var filename = '';
	var res = /[\/\\]([^\/\\]+)$/.exec(e.getValue());
	if (res) {
		filename = res[1];
	} else {
		filename = e.getValue();
	}
	fnf.set({
		value: filename
	});
	// detect values for other fields

	var types = [ [ /\.JPEG$/i, 'image/jpeg' ], [ /\.JPG$/i, 'image/jpeg' ],
			[ /\.PNG$/i, 'image/png' ], [ /\.GIF$/i, 'image/gif' ] ];

	var content_type = '';
	Ext.each(types, function(t) {
		if (t[0].exec(filename)) {
			content_type = t[1];
			return false;
		}
	});

	switch (content_type) {
	case 'image/jpeg':
	case 'image/png':
	case 'image/gif':
		dltf.dom.selectedIndex = 1;
		break;

	default:
		dltf.dom.selectedIndex = 0;
	}

	if (content_type === '') {
		content_type = 'application/octet-stream';
	}
	
	fnf.focus();
};

Pyrone.file.listDeleteSelected = function(table_id, url) {
	// find all checkboxes in the table
	var selected_uids = Pyrone.getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		return;
	}
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: {
			uids: selected_uids.join(',')
		},
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			Ext.each(json.deleted, function(id) {
				// delete rows
				var e = $e('list-tr-'+id);
				e.setVisibilityMode(Ext.Element.DISPLAY);
				e.hide(true);
			});
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.file.listDeleteSelectedReq = function(table_id, url) {
	var selected_uids = Pyrone.getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		Pyrone.createLinkNotifyBox('delete-selected-btn', tr('SELECT_ITEMS_FIRST'));
		return;
	}
	// ask confirmation
	Pyrone.createConfirmLink('delete-selected-btn', function() {Pyrone.file.listDeleteSelected(table_id, url);});
};

Pyrone.settings.saveSettings = function(url) {
	var field_names = ['site_title', 'site_base_url', 'site_copyright', 'elements_on_page',
	              'admin_notifications_email', 'notifications_from_email', 'verification_msg_subject_tpl',
	              'comment_answer_msg_subject_tpl', 'comment_answer_msg_body_tpl',
	              'verification_msg_body_tpl', 'image_preview_width', 'google_analytics_id',
                  'timezone',
	              'admin_notify_new_comment_subject_tpl', 'admin_notify_new_comment_body_tpl',
	              'admin_notify_new_user_subject_tpl', 'admin_notify_new_user_body_tpl',
	              'tw_consumer_key', 'tw_consumer_secret'];
	var bool_field_names = ['admin_notify_new_comments', 'admin_notify_new_user']
	var params = {};
	
	Ext.each(field_names, function(field_name) {
		var e = $e('fid-'+field_name);
		params[field_name] = e.getValue();
	});
	Ext.each(bool_field_names, function(field_name) {
		var e = $e('fid-'+field_name);
		if (e.dom.checked) {
			params[field_name] = true;
		}
	});
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: params,
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			if (json.errors) {
				var focus_el = false;
				Ext.each(field_names, function(field_name) {
					var error_value = json.errors[field_name],
						error_el = $e('error-'+field_name);
					
					if (error_value) {
						if (!focus_el) {
							focus_el = $e('fid-'+field_name);
						};
						Pyrone.notify(error_el, error_value, false, -1);
					} else {
						Pyrone.unnotify(error_el);
					}
				});
				if (focus_el) {
					focus_el.focus();
				}
			} else {
				Pyrone.notify($e('eid-notify'), tr('SETTINGS_SAVED'), false, 20000);
			}
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});	
};

Pyrone.settings.widgets.pagesSave = function(url) {
	var e = $e('fid-widget_pages_pages_spec')
		widget_pages_pages_spec = e.getValue();
	
	var params = {
		widget_pages_pages_spec: widget_pages_pages_spec
	};
	
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: params,
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			if (json.errors) {
			} else {
				Pyrone.notify($e('eid-notify'), tr('SETTINGS_SAVED'), false, 20000);
			}
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});	
};

Pyrone.account.listDeleteSelected = Pyrone.file.listDeleteSelected;
Pyrone.backup.listDeleteSelected = Pyrone.file.listDeleteSelected;
/*
Pyrone.account.listDeleteSelected = function(table_id, url) {
	// find all checkboxes in the table
	var selected_uids = Pyrone.getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		return;
	}
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: {
			uids: selected_uids.join(',')
		},
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			Ext.each(json.deleted, function(id) {
				// delete rows
				var e = $e('list-tr-'+id);
				e.setVisibilityMode(Ext.Element.DISPLAY);
				e.hide(true);
			});
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};
*/

Pyrone.account.listDeleteSelectedReq = function(table_id, url) {
	var selected_uids = Pyrone.getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		Pyrone.createLinkNotifyBox('delete-selected-btn', tr('SELECT_ITEMS_FIRST'));
		return;
	}
	// ask confirmation
	Pyrone.createConfirmLink('delete-selected-btn', function() {Pyrone.file.listDeleteSelected(table_id, url);});
};

Pyrone.account.changeEmailVerified = function(email_id, new_state/*true|false*/, url) {
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: {
			id: email_id,
			is_verified: new_state ? 'true' : 'false'
		},
		success: function(response, opts) {
			//var json = Ext.decode(response.responseText);
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.backup.listDeleteSelectedReq = function(table_id, url) {
	var selected_uids = Pyrone.getSelectedRows(table_id);
	if (selected_uids.length == 0) {
		Pyrone.createLinkNotifyBox('delete-selected-btn', tr('SELECT_ITEMS_FIRST'));
		return;
	}
	// ask confirmation
	Pyrone.createConfirmLink('delete-selected-btn', function() {Pyrone.backup.listDeleteSelected(table_id, url);});
};

Pyrone.backup.backupNow = function(url) {
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: {
		},
		success: function(response, opts) {
			//var json = Ext.decode(response.responseText);
			//console.log(json.backup_file);
			location.reload(true);
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.backup.startRestore = function(url) {
	// display mask layer or something like
	
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: {
		},
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			if (json.error) {
				$e('eid-error').update(json.error);
				$show('eid-error', true);
				$hide.defer(5000, window, ['eid-error', true]);
				return;
			}
			//console.log(json.backup_file);
			// remove mask
			alert(tr('BACKUP_RESTORE_COMPLETE'));
			location.assign('/');
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.backup.startRestoreReq = function(url, restore_link_id) {
	// ask confirmation
	Pyrone.createConfirmLink(restore_link_id, function() {Pyrone.backup.startRestore(url);});
};
