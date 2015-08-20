// vim: noexpandtab
function tr(phrase_id) {
	if (Pyrone_tr && Pyrone_tr[phrase_id]) {
		return Pyrone_tr[phrase_id];
	} else {
		console.log('fail');
		return phrase_id;
	}
}

/*
function _cl(lang) {
    document.cookie = 'ui_lang='+lang+'; EXPIRES=Wed, 01 Jan 2020 00:00:00 UTC; PATH=/';
    document.location.reload(true);
    return false;
}
*/

function Pyrone_lang_set(lang_code) {
    document.cookie = 'ui_lang='+lang_code+'; EXPIRES=Wed, 01 Jan 2120 00:00:00 UTC; PATH=/';
    document.location.reload(true);
}

/**
 * Update element text, show it and then hide after timeout
 */
function Pyrone_notify(elem, text, afterfunc, timeout) {
	if (!timeout) {
		timeout = 3000;
	}
	elem.html(text);
	elem.slideDown(300).delay(timeout).slideUp(300);
}

/** 
 * Return list of selected rows in the table
 *
 * @param {String} table element id.
 * @return {Array} list of selected rows.
 */
function Pyrone_getSelectedRows(table_id) {
	var table = $('#'+table_id);
	if (!table.get(0)) {
		return false;
	}
	
	var nodes = table.find('input[class=list-cb]'),
		res = [];

	nodes.each(function(ind, el) {
		if (el.checked) {
			res.push(el.value);
		}
	});
	return res;
}

function Pyrone_selectDeselectAll(table_id)
{
	var table = $('#'+table_id);
	if (!table.get(0)) {
		return false;
	}

	var nodes = table.find('input[class=list-cb]').filter('[disabled!=disabled]'),
		checked_count = 0,
		not_checked_count = 0;

	nodes.each(function(ind, el) {
		if (el.checked) {
			checked_count++;
		} else {
			not_checked_count++;
		}
	});

	var new_state;

	if (checked_count > 0 && not_checked_count == 0) {
		// i.e. all rows selected, so clear selection
		new_state = false;
	} else {
		// select all otherwise
		new_state = true;
	}
	nodes.prop('checked', new_state);
}


/**
 * @param {String} target_id id of node where append confirm box
 * @param {Function} callback required callback to be called when user clicks confirm box
 */
 function Pyrone_createConfirmLink(target_id, callback) {
	var confirm_id = 'confirmlink-' + target_id;
	if ($('#'+confirm_id).get(0)) {
		return;
	}

	var target = document.getElementById(target_id);
	if (!target) {
		return;
	}
	target = $(target);

	var confirmation_el = $('<a>⇒ OK</a>').attr({
		href: '#',
		id: confirm_id
	}).addClass('confirm-icon')
	  .click(function(e) {
	  	  callback.call();
	  	  confirmation_el.remove();
	  	  return false;
	  });
	target.after(confirmation_el);

	setTimeout(function(){
		confirmation_el.remove();
	}, 1000);
}

/**
 * Display information box appended to specified target
 */
 function Pyrone_createLinkNotifyBox(target_id, message) {
	var notify_id = 'notifybox-' + target_id;
	if ($('#'+notify_id).get(0)) {
		return;
	}
	var target = $('#'+target_id);
	if (!target.get(0)) {
		return;
	}

	var notify_el = $('<SPAN></SPAN>').attr({
		href: '#',
		id: notify_id
	}).text(message).addClass('notify-icon')
	  .click(function(e) {
	  	  notify_el.remove();
	  	  return false;
	  });
	target.after(notify_el);

	setTimeout(function(){
		notify_el.remove();
	}, 1000);
}


/**
 * Display preview of composing article
 */
function Pyrone_article_preview() {
	// send AJAX request to the server and display received (and rendered) article body text
	var body = $('#fid-body').val();

	$.ajax({
		url: '/preview/article',
		type: 'POST',
		data: {
			body: body
		}
	}).done(function(data) {
		var e = $('#eid-article-render-preview');
		e.show('slow').html(data);
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

/**
 * Save article using AJAX request
 */
function Pyrone_article_save(url) {
	var save_button = $('#eid-save-button');
	save_button.attr('disabled', 'disabled');

	var params = {
		title: $('#fid-title').val(),
		shortcut: $('#fid-shortcut').val(),
		published: $('#fid-published').val(),
		tags: $('#fid-tags').val(),
		body: $('#fid-body').val()
	};

	if ($('#fid-is_draft').prop('checked')) {
		params['is_draft'] = 1;
	}
	if ($('#fid-is_commentable').prop('checked')) {
		params['is_commentable'] = 1;
	}

	$.ajax({
		url: url,
		type: 'POST',
		data: params,
		dataType: 'json'
	}).done(function(data) {
		if (!data.errors) {
			Pyrone_notify($('#eid-article-notify'), tr('ARTICLE_SAVED'));
		}
		save_button.removeAttr('disabled');
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
		save_button.removeAttr('disabled');
	});
}

function Pyrone_article_deleteArticle(url, article_id) {
	$.ajax({
		url: url,
		type: 'POST',
		dataType: 'json'
	}).done(function(data) {
		window.location.reload(true);
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
		save_button.removeAttr('disabled');
	});
}

function Pyrone_article_deleteArticleReq(url, article_id) {
	Pyrone_createConfirmLink('a-d-'+article_id, function() { Pyrone_article_deleteArticle(url, article_id);});
}

/**
 * Post comment using AJAX request
 */
function Pyrone_article_postComment() {
	var body = $('#fid-comment-body').val();
	var e = $('#eid-comment-error');
	
	if (body == '') {
		var body_el = $('#fid-comment-body');
		body_el.focus();
		Pyrone_notify(e, tr('COMMENT_BODY_IS_REQUIRED'));
		return;
	}
	
	var f = $('#eid-comment-form'),
		url = f.prop('action') + '/ajax',
		article_id = $('#fid-article_id').val(),
		parent = $('#fid-parent-comment').val(),
		display_name = $('#fid-comment-displayname').val(),
		email = $('#fid-comment-email').val(),
		website = $('#fid-comment-website').val(),
		is_subscribed = $('#fid-is_subscribed').prop('checked');
	
	var params = {s: article_id};
	params[article_id.substring(3, 14)] = body;
	params[article_id.substring(4, 12)] = parent;
	params[article_id.substring(0, 5)] = display_name;
	params[article_id.substring(13, 25)] = email;
	params[article_id.substring(15, 21)] = website;
	if (typeof is_subscribed != 'undefined') {
		params[article_id.substring(19, 27)] = 'true';
	}
	
	var display_name_field = $('#fid-comment-displayname');
	
	if (display_name_field.prop('type') == 'text' && display_name == '') {
		display_name_field.focus();
		Pyrone_notify(e, tr('COMMENT_DISPLAY_NAME_IS_REQUIRED'));
		return;
	}
	
	var disable_ids = ['fid-comment-displayname', 'fid-comment-email', 'fid-comment-website',
		'fid-comment-body', 'eid-post-comment-button', 'fid-is_subscribed'];

	function setFieldsDisabled(disable) {
		$.each(disable_ids, function(ind, fid) {
			$('#'+fid).prop('disabled', disable);
		});
	}

	setFieldsDisabled(true);
	var backup_button_title = $('#eid-post-comment-button').val();

	$('#eid-post-comment-button').val(tr('POSTING_COMMENT'));
	$('body').css('cursor', 'progress');

	$.ajax({
		url: url,
		type: 'POST',
		data: params,
		dataType: 'json'
	}).done(function(json) {
		if (json.error) {
			alert(json.error);
			setFieldsDisabled(false);
			$('#eid-post-comment-button').val(backup_button_title);
			$('body').css('cursor', 'default');
			return;
		}
		if (!json.approved) {
			// clear fields
			$('#fid-comment-body').val('');
			Pyrone_notify($('#eid-comment-notify'), 
				tr('COMMENT_IS_WAITING_FOR_APPROVAL'), $.noop, 10000);
			// display alert
		} else {
			window.location.replace(json.url);
		}		
	}).fail(function(){
		alert(tr('AJAX_REQUEST_ERROR'));
		setFieldsDisabled(false);
		$('#eid-post-comment-button').val(backup_button_title);
		$('body').css('cursor', 'default');
	});
}

/**
 * reply to specific comment: move comment form to corresponding comment element
 */
function Pyrone_article_replyToComment(comment_id) {
	var comment_block = $('#c-'+comment_id),
		comment_form = $('#eid-comment-form'),
		link = $('#eid-leave-comment-link-bottom'),
		parent_comment_field = $('#fid-parent-comment');
	
	if (!comment_block.get(0)) {
		return;
	}
	comment_block.append(comment_form);
	
	if (comment_id === -1) {
		link.hide(0);
		parent_comment_field.val('');
	} else {
		parent_comment_field.val(comment_id);
		link.show(0);
	}
	$('#fid-comment-body').focus();
}

function Pyrone_article_approveComment(url, comment_id) {
	$.ajax({
		url: url,
		type: 'POST'
	}).done(function() {
		// mark corresponding comment as approved
		var c_el = $('#c-'+comment_id),
			ca_el = $('#ca-'+comment_id);
		if (c_el) {
			c_el.removeClass('not-approved');
		}
		if (ca_el) {
			ca_el.hide(0);
		}

	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

function Pyrone_article_deleteComment(url, comment_id) {
	$.ajax({
		url: url,
		type: 'POST'
	}).done(function() {
		// delete correspondig comment block
		var c_el = $('#c-'+comment_id);
		c_el.css('background-color', '#f33');
		c_el.hide(0);
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

function Pyrone_article_deleteCommentReq(url, comment_id) {
	Pyrone_createConfirmLink('cd-'+comment_id, function() { Pyrone_article_deleteComment(url, comment_id); });
}


/**
 * Display comment editing form
 */
function Pyrone_article_showEditCommentForm(url, url_fetch, comment_id) {
	// replace comment element with editing form
	var inner = $('#c-inner-'+comment_id),
		comment_el = $('#c-'+comment_id),
		edit_form = $('#c-edit');
	
	// start loading comment data
	$.ajax({
		url: url_fetch,
		dataType: 'json',
		type: 'POST'
	}).done(function(json){
		// fill form fields and show form
		$('#c-edit-comment_id').val(comment_id);
		$('#c-edit-body').val(json.body);
		$('#c-edit-name').val(json.display_name);
		$('#c-edit-email').val(json.email);
		$('#c-edit-website').val(json.website);
		$('#c-edit-date').val(json.date);
		$('#c-edit-ip').val(json.ip_address);
		$('#c-edit-xffip').val(json.xff_ip_address);
		$('#c-edit-is_subscribed').prop('checked', json.is_subscribed === true);
		inner.hide(0);
		comment_el.append(edit_form);
		edit_form.show();
	}).fail(function(){
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

function Pyrone_article_submitEditCommentForm(url_template) {
	var comment_id = $('#c-edit-comment_id').val();
	
	if (comment_id == '') {
		return;
	}
	
	var submit_url = url_template.replace(/666/, comment_id),
		params = {},
		fields = ['body', 'name', 'email', 'website', 'date', 'ip', 'xffip'];
	
	$.each(fields, function(ind, fn) {
		params[fn] = $('#c-edit-'+fn).val();
	});
	
	if ($('#c-edit-is_subscribed').prop('checked')) {
		params['is_subscribed'] = 'true';
	}
	
	$.ajax({
		url: submit_url,
		type: 'POST',
		data: params,
		dataType: 'json'
	}).done(function(json) {
		inner = $('#c-inner-'+comment_id),
		edit_form = $('#c-edit');
	
		edit_form.hide(0);
		inner.show(0);
		
		// re-render comment
		if (json.rendered) {
			inner.html(json.rendered);
		}
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

function Pyrone_article_cancelEditCommentForm() {
	var comment_id = $('#c-edit-comment_id').val(),
		inner = $('#c-inner-'+comment_id),
		edit_form = $('#c-edit');
	
	edit_form.hide(0);
	inner.show(0);
}

function Pyrone_account_logout(url) {
	$.ajax({
		url: url,
		type: 'POST'
	}).done(function(){
		window.location.replace('/');
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

function Pyrone_account_loginTwitter(url) {
	if (window.document.location.href.toLowerCase().indexOf('http://') != -1) {
		alert(tr('TWITTER_AUTH_REQUIRES_HTTPS'));
		return;
	}
	$.ajax({
		url: url,
		type: 'POST',
		data: {
			page_url: window.location.href
		},
		dataType: 'json'
	}).done(function(json) {
		// json.authorize_url contains authorization url that should
		// be opened in browser window
		if (json.error) {
			alert(json.error);
			return;
		}
		if (!json.authorize_url) {
			alert(tr('TWITTER_AUTH_IS_NOT_WORKING'));
			return;
		}
		// open new window with just provided url
		window.location.assign(json.authorize_url);
		//alert(json.authorize_url);
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

// stub
function Pyrone_article_checkForm()
{
	return true;
}

function Pyrone_article_expandModeratedComment(comment_id) {
	var collapsed_el = $('#c-c-'+comment_id),
		expanded_el = $('#c-e-'+comment_id);
	if (!collapsed_el.get(0) && !expanded_el.get(0)) {
		return;
	}
	collapsed_el.hide(0);
	expanded_el.show(0);
}

function Pyrone_article_approveModeratedComment(url, comment_id) {
	var comment_el = $('#c-'+comment_id);
	$.ajax({
		url: url,
		type: 'POST'
	}).done(function() {
		// delete approved comment from the list
		comment_el.remove();
	}).fail(function() {
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

Pyrone_article_deleteModeratedComment = Pyrone_article_deleteComment;

function Pyrone_article_deleteModeratedCommentReq(url, comment_id) {
	Pyrone_createConfirmLink('cd-'+comment_id, function() { Pyrone_article_deleteModeratedComment(url, comment_id); });
}

function Pyrone_account_saveMyProfile(url)
{
	$.each(['email', 'display_name', 'password_1'], function (ind, n) {
		// hide all error messages
		$('#error-'+n).hide(0);
	});
	// first check params
	var login_field = $('#fid-login'),
		is_error = false;
	if (login_field) {
		var v = login_field.val(),
			e = $('#error-login'),
			error = '';
		if (v == '') {
			error = tr('FIELD_IS_REQUIRED');
		} else if (!/^[a-zA-Z0-9]+$/.test(v)) {
			error = tr('FIELD_MUST_BE_ALPHA_NUM');
		}
		if (error != '') {
			is_error = true;
			e.html(error);
			e.show(0);
			login_field.focus();
		}
	}
	
	var display_name_field = $('#fid-display_name');
	if (display_name_field) {
		var v = display_name_field.val(),
		e = $('#error-display_name'),
		error = '';
		if (v == '') {
			error = tr('FIELD_IS_REQUIRED');
		}
		if (error != '') {
			is_error = true;
			e.html(error).show(0);
			display_name_field.focus();
		}
	}
	
	var email_field = $('#fid-email');
	
	if (is_error) {
		return;
	}
	
	var p1 = $('#fid-password_1').val(),
		p2 = $('#fid-password_2').val();
	
	if (p1 && p2) {
		if (p1 != p2 && (p1 != '' || p2 != '')) {
			is_error = true;
			var e = $('#error-password_1');
			e.html(tr('PASSWORDS_DONT_MATCH')).show(0);
		}
	}
	
	var params = {};
	
	if (email_field.get(0)) {
		params['email'] = email_field.val();
	}
	if (login_field.get(0)) {
		params['login'] = login_field.val();
	}
	if (display_name_field.get(0)) {
		params['display_name'] = display_name_field.val();
	}
	if (p1) {
		params['new_password'] = p1;
	}
	
	$.ajax({
		url: url,
		type: 'POST',
		data: params,
		dataType: 'json'
	}).done(function() {
		Pyrone_notify($('#eid-notify'), tr('YOUR_PROFILE_HAS_BEEN_UPDATED'));
	}).fail(function(){
		alert(tr('AJAX_REQUEST_ERROR'));
	});
}

function Pyrone_editor_unindent(id)
{
	var f = $('#'+id);

	if (f.length == 0) {
		return;
	}

	var sel = f.fieldSelection();

	if (sel.length == 0) {
		return;
	}

	var field_value = f.val(),
		c;

	if (sel.start != 0) {
		// i.e. text starts somewhere in the middle
		c = field_value.charCodeAt(sel.start - 1);
		if (c != 10 && c != 13) {
			return;
		}
	}

	// now detect is it possible to unindent the selection
	// split into the lines and look at the starting characters on each line
	var lines = sel.text.split(/(?:\r\n|\r|\n)/m),
		success = true,
		result = [],
		indent_type = false,
		indent;

	$.each(lines, function(ind, line) {
		if (line.length == 0) {
			result.push(line);
			return;
		}

		switch (indent_type) {
		case false:
			if (line.charAt(0) == '\t') {
				indent_type = 'tab';
				line = line.substr(1);
				break;
			}
			indent = line.substr(0, 4);
			// it has to be exactly 4-spaces, otherwise we cannot procede
			if (indent != '    ') {
				success = false;
				return false;
			}
			indent_type = 'space';
			line = line.substr(4);
			break;

		case 'tab':
			if (line.charAt(0) != '\t') {
				success = false;
				return false;
			}
			line = line.substr(1);
			break;

		case 'space':
			indent = line.substr(0, 4);
			if (indent != '    ') {
				success = false;
				return false;
			}
			line = line.substr(4);
			break;
		}

		result.push(line);
	});

	if (success === true) {
		var new_selection = result.join('\n');
		f.fieldSelection(new_selection);
	}
}

function Pyrone_editor_indent(id)
{
	var f = $('#'+id);

	if (f.length == 0) {
		return;
	}

	var sel = f.fieldSelection();

	if (sel.length == 0) {
		return;
	}

	var field_value = f.val(),
		c;

	if (sel.start != 0) {
		// i.e. text starts somewhere in the middle of line
		c = field_value.charCodeAt(sel.start - 1);
		if (c != 10 && c != 13) {
			return;
		}
	}

	var result = [];

	$.each(sel.text.split(/(?:\r\n|\r|\n)/m), function(ind, line) {
		result.push('    ' + line);
	});

	var new_selection = result.join('\n');
	f.fieldSelection(new_selection);
}

function Pyrone_editor_wrap(id, wrap_in)
{
	var f = $('#'+id),
		sel = f.fieldSelection();

	if (sel.length == 0) {
		return;
	}

	var text = wrap_in + sel.text + wrap_in;

	f.fieldSelection(text);
}

function Pyrone_editor_blockquote(id)
{
	var f = $('#'+id);

	if (f.length == 0) {
		return;
	}

	var sel = f.fieldSelection();

	if (sel.length == 0) {
		return;
	}

	var field_value = f.val(),
		c;

	if (sel.start != 0) {
		// i.e. text starts somewhere in the middle of line
		c = field_value.charCodeAt(sel.start - 1);
		if (c != 10 && c != 13) {
			return;
		}
	}

	var result = [];

	$.each(sel.text.split(/(?:\r\n|\r|\n)/m), function(ind, line) {
		result.push('> ' + line);
	});

	var new_selection = result.join('\n');
	f.fieldSelection(new_selection);
}