// vim: noexpandtab
function tr(phrase_id) {
	if (Pyrone.tr && Pyrone.tr[phrase_id]) {
		return Pyrone.tr[phrase_id];
	} else {
		console.log('fail');
		return phrase_id;
	}
}

Ext.ns('Pyrone');
Ext.ns('Pyrone.article');
Ext.ns('Pyrone.lang');
Ext.ns('Pyrone.account');
/*
function _cl(lang) {
    document.cookie = 'ui_lang='+lang+'; EXPIRES=Wed, 01 Jan 2020 00:00:00 UTC; PATH=/';
    document.location.reload(true);
    return false;
}
*/

Pyrone.lang.set = function(lang_code) {
    document.cookie = 'ui_lang='+lang_code+'; EXPIRES=Wed, 01 Jan 2120 00:00:00 UTC; PATH=/';
    document.location.reload(true);
};

/**
 * Update element text, show it and then hide after timeout
 */
Pyrone.notify = function(elem, text, afterfunc, timeout) {
	if (!timeout) {
		timeout = 3000;
	}
	elem.setVisibilityMode(Ext.Element.DISPLAY);
	elem.show(true);
	elem.update(text);
	if (timeout > 0) {
		(function(){ elem.hide(true); if (afterfunc) {afterfunc.call(); } }).defer(timeout);
	}
};

/** 
 * Return list of selected rows in the table
 */
Pyrone.getSelectedRows = function(table_id) {
	var table = $e(table_id);
	if (!table) {
		return false;
	}
	
	var nodes = table.query('input[class=list-cb]'),
		res = [];
	Ext.each(nodes, function(node) {
		if (node.checked) {
			res.push(node.value);
		}
	});
	return res;
};

Pyrone.unnotify = function(elem) {
	if (elem) {
		elem.hide(true);
	}
};

/**
 * @param {String} target_id id of node where append confirm box
 * @param {Function} callback required callback to be called when user clicks confirm box
 */
Pyrone.createConfirmLink = function(target_id, callback) {
	var confirm_id = 'confirmlink-' + target_id;
	if ($e(confirm_id)) {
		return;
	}
	
	var target = $e(target_id);
	if (!target) {
		return;
	}
	var e = document.createElement('A');
	e.innerHTML = '⇒ OK';
	e.href = '#';
	e.id = confirm_id;
	var confirmation_el;
	e.onclick = function() { callback.call(); confirmation_el.remove(); return false; };
	confirmation_el = new Ext.Element(e);
	confirmation_el.addClass('confirm-icon');
	confirmation_el.insertAfter(target);
	// set timeout and delete
	(function() {confirmation_el.remove();}).defer(1000);
};

/**
 * Display information box appended to specified target
 */
Pyrone.createLinkNotifyBox = function(target_id, message) {
	var notify_id = 'notifybox-' + target_id;
	if ($e(notify_id)) {
		return;
	}
	var target = $e(target_id);
	if (!target) {
		return;
	}
	var e = document.createElement('SPAN');
	e.innerHTML = message;
	e.id = notify_id;
	var notify_el;
	e.onclick = function() {notify_el.remove();};
	notify_el = new Ext.Element(e);
	notify_el.addClass('notify-icon');
	notify_el.insertAfter(target);
	// set timeout and delete
	(function() {notify_el.remove();}).defer(3000);
};

window.$ev = function(field) {
	if (typeof field == 'string') {
		field = Ext.get(field);
		if (!field) {
			return false;
		}
	}
	return field.getValue();
};

window.$e = function(fid) {
	return Ext.get(fid);
};

window.$sev = function(field, value) {
	if (typeof field == 'string') {
		field = Ext.get(field);
	}
	//return field.set({value: value});
	field.dom.value = value;
};

window.$hide = function(el, anim) {
	if (typeof el == 'string') {
		el = $e(el);
	}
	if (!el) {
		return false;
	}
	el.setVisibilityMode(Ext.Element.DISPLAY);
	el.hide(anim);
};

window.$show = function(eid, anim) {
	var el = $e(eid);
	if (!el) {
		return false;
	}
	el.setVisibilityMode(Ext.Element.DISPLAY);
	el.show(anim);
}

Pyrone.article.checkForm = function() {
	return true;
};

/**
 * Display preview of composing article
 */
Pyrone.article.preview = function() {
	// send AJAX request to the server and display received (and rendered) article body text
	var body = Ext.get('fid-body').getValue();
	Ext.Ajax.request({
		url: '/preview/article',
		method: 'POST',
		params: {
			body: body
		},
		success: function(response, opts) {
			var e = Ext.get('eid-article-preview');
			e.show(true);
			e.update(response.responseText);
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

/**
 * Save article using AJAX request
 */
Pyrone.article.save = function(url) {
	$e('eid-save-button').dom.disabled = true;
	var params = {
		title: $ev('fid-title'),
		shortcut: $ev('fid-shortcut'),
		published: $ev('fid-published'),
		tags: $ev('fid-tags'),
		body: $ev('fid-body')
	};

	if ($e('fid-is_draft').dom.checked) {
		params['is_draft'] = 1;
	}
	if ($e('fid-is_commentable').dom.checked) {
		params['is_commentable'] = 1;
	}

	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: params,
		success: function(response, opts) {
			// parse response to JSON
			var data = Ext.decode(response.responseText);
			if (!data.errors) {
				Pyrone.notify($e('eid-article-notify'), tr('ARTICLE_SAVED'));
			} else {
				var e;
				Pyrone.notify($e('eid-article-warning'), tr('ARTICLE_NOT_SAVED'));
				for (fn in data.errors) {
					e = $e('error-'+fn);
					if (e) {
						e.dom.innerHTML = data.errors[fn];
						$show(e);
					}
				}
			}
			$e('eid-save-button').dom.disabled = false;
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
			$e('eid-save-button').dom.disabled = false;
		}
	});
};

Pyrone.article.deleteArticle = function(url, article_id) {
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		success: function(response, opts) {
			window.location.reload(true);
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});	
};

Pyrone.article.deleteArticleReq = function(url, article_id) {
	Pyrone.createConfirmLink('ad-'+article_id, function() { Pyrone.article.deleteArticle(url, article_id);});
};

/**
 * Post comment
 */
Pyrone.article.postComment = function() {
	var body = Ext.get('fid-comment-body').getValue();
	
	var e = Ext.get('eid-comment-error');
	
	if (body == '') {
		var body_el = Ext.get('fid-comment-body');
		body_el.focus();
		Pyrone.notify(e, tr('COMMENT_BODY_IS_REQUIRED'));
		return;
	}
	
	var f = Ext.get('eid-comment-form'),
		url = f.dom.action + '/ajax',
		article_id = $ev('fid-article_id'),
		parent = $ev('fid-parent-comment'),
		display_name = $ev('fid-comment-displayname'),
		email = $ev('fid-comment-email'),
		website = $ev('fid-comment-website'),
		is_subscribed = $e('fid-is_subscribed').dom.checked;
	
	var params = {s: article_id};
	params[article_id.substring(3, 14)] = body;
	params[article_id.substring(4, 12)] = parent;
	params[article_id.substring(0, 5)] = display_name;
	params[article_id.substring(13, 25)] = email;
	params[article_id.substring(15, 21)] = website;
	if (is_subscribed) {
		params[article_id.substring(19, 27)] = 'true';
	}
	
	var display_name_field = $e('fid-comment-displayname');
	
	if (display_name_field.getAttribute('type') == 'text' && display_name == '') {
		display_name_field.focus();
		Pyrone.notify(e, tr('COMMENT_DISPLAY_NAME_IS_REQUIRED'));
		return;
	}
	
	Ext.Ajax.request({
		url: url,
		params: params,
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			if (json.error) {
				alert(json.error);
				return;
			}
			if (!json.approved) {
				// clear fields
				$e('fid-comment-body').dom.value = '';
				Pyrone.notify($e('eid-comment-notify'), tr('COMMENT_IS_WAITING_FOR_APPROVAL'), Ext.emptyFn, 10000);
				// display alert
			} else {
				window.location.replace(json.url);
			}
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

/**
 * reply to specific comment: move comment form to corresponding comment element
 */
Pyrone.article.replyToComment = function(comment_id) {
	var comment_block = $e('c-'+comment_id),
		comment_form = $e('eid-comment-form'),
		link = $e('eid-leave-comment-link-bottom'),
		parent_comment_field = $e('fid-parent-comment');
	
	if (!comment_block) {
		return;
	}
	comment_block.appendChild(comment_form);
	
	if (comment_id === -1) {
		link.setDisplayed(false);
		$sev(parent_comment_field, '');
	} else {
		$sev(parent_comment_field, comment_id);
		link.setDisplayed(true);
	}
	$e('fid-comment-body').focus();
};

Pyrone.article.approveComment = function(url, comment_id) {
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		success: function(response, opts) {
			// mark corresponding comment as approved
			var c_el = $e('c-'+comment_id),
				ca_el = $e('ca-'+comment_id);
			if (c_el) {
				c_el.removeClass('not-approved');
			}
			if (ca_el) {
				ca_el.setVisibilityMode(Ext.Element.DISPLAY);
				ca_el.hide(true);
			}
			
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.article.deleteComment = function(url, comment_id) {
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		success: function(response, opts) {
			// delete correspondig comment block
			var c_el = $e('c-'+comment_id);
			c_el.setStyle('background-color', '#f33');
			c_el.setVisibilityMode(Ext.Element.DISPLAY);
			c_el.hide(true);
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.article.deleteCommentReq = function(url, comment_id) {
	Pyrone.createConfirmLink('cd-'+comment_id, function() { Pyrone.article.deleteComment(url, comment_id); });
};


/**
 * Display comment editing form
 */
Pyrone.article.showEditCommentForm = function(url, url_fetch, comment_id) {
	// replace comment element with editing form
	var inner = $e('c-inner-'+comment_id),
		comment_el = $e('c-'+comment_id),
		edit_form = $e('c-edit');
	edit_form.setVisibilityMode(Ext.Element.DISPLAY);
	
	// start loading comment data
	Ext.Ajax.request({
		url: url_fetch,
		method: 'POST',
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			// fill form fields and show form
			$sev('c-edit-comment_id', comment_id);
			$sev('c-edit-body', json.body);
			$sev('c-edit-name', json.display_name);
			$sev('c-edit-email', json.email);
			$sev('c-edit-website', json.website);
			$sev('c-edit-date', json.date);
			$sev('c-edit-ip', json.ip_address);
			$sev('c-edit-xffip', json.xff_ip_address);
			$e('c-edit-is_subscribed').dom.checked = json.is_subscribed === true;
			$hide(inner);
			comment_el.appendChild(edit_form);
			edit_form.show();
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
	
	
};

Pyrone.article.submitEditCommentForm = function(url_template) {
	var comment_id = $ev('c-edit-comment_id');
	
	if (comment_id == '') {
		return;
	}
	
	var submit_url = url_template.replace(/666/, comment_id),
		params = {},
		fields = ['body', 'name', 'email', 'website', 'date', 'ip', 'xffip'];
	
	Ext.each(fields, function(fn) {
		params[fn] = $ev('c-edit-'+fn);
	});
	
	if ($e('c-edit-is_subscribed').dom.checked) {
		params['is_subscribed'] = 'true';
	}
	
	Ext.Ajax.request({
		url: submit_url,
		method: 'POST',
		params: params,
		success: function(response, opts) {
			var json = Ext.decode(response.responseText),
			inner = $e('c-inner-'+comment_id),
			edit_form = $e('c-edit');
		
			edit_form.hide();
			inner.show();
			
			// re-render comment
			if (json.rendered) {
				//console.log(json.rendered, inner.dom.innerHTML);
				inner.dom.innerHTML = json.rendered;
			}
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
			
};

Pyrone.article.cancelEditCommentForm = function() {
	var comment_id = $e('c-edit-comment_id').getValue(),
		inner = $e('c-inner-'+comment_id),
		edit_form = $e('c-edit');
	
	edit_form.hide();
	inner.show();
};

Pyrone.account.logout = function(url) {
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		success: function(response, opts) {
			location.reload(true);
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.account.loginTwitter = function(url) {
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: {
			page_url: window.location.href
		},
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
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
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.article.expandModeratedComment = function (comment_id) {
	var collapsed_el = $e('c-c-'+comment_id),
		expanded_el = $e('c-e-'+comment_id);
	if (!collapsed_el && !expanded_el) {
		return;
	}
	$hide(collapsed_el);
	$show(expanded_el);
};

Pyrone.article.approveModeratedComment = function(url, comment_id) {
	var comment_el = $e('c-'+comment_id);
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		success: function(response, opts) {
			// delete approved comment from the list
			if (comment_el) {
				$hide(comment_el);
			}
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

Pyrone.article.deleteModeratedComment = Pyrone.article.deleteComment;

Pyrone.article.deleteModeratedCommentReq = function(url, comment_id) {
	Pyrone.createConfirmLink('cd-'+comment_id, function() { Pyrone.article.deleteModeratedComment(url, comment_id); });
};

Pyrone.account.saveMyProfile = function(url)
{
	Ext.each(['email', 'display_name', 'password_1'], function (n) {
		// hide all error messages
		$hide('error-'+n);
	});
	// first check params
	var login_field = $e('fid-login'),
		is_error = false;
	if (login_field) {
		var v = $ev(login_field),
			e = $e('error-login'),
			error = '';
		if (v == '') {
			error = tr('FIELD_IS_REQUIRED');
		} else if (!/^[a-zA-Z0-9]+$/.test(v)) {
			error = tr('FIELD_MUST_BE_ALPHA_NUM');
		}
		if (error != '') {
			is_error = true;
			e.dom.innerHTML = error;
			$show(e);
			login_field.focus();
		}
	}
	
	var display_name_field = $e('fid-display_name');
	if (display_name_field) {
		var v = $ev(display_name_field),
		e = $e('error-display_name'),
		error = '';
		if (v == '') {
			error = tr('FIELD_IS_REQUIRED');
		}
		if (error != '') {
			is_error = true;
			e.dom.innerHTML = error;
			$show(e);
			display_name_field.focus();
		}
	}
	
	var email_field = $e('fid-email');
	
	if (is_error) {
		return;
	}
	
	var p1 = $ev('fid-password_1'),
		p2 = $ev('fid-password_2');
	
	if (p1 && p2) {
		if (p1 != p2 && (p1 != '' || p2 != '')) {
			is_error = true;
			var e = $e('error-password_1');
			e.dom.innerHTML = tr('PASSWORDS_DONT_MATCH');
			$show(e);
		}
	}
	
	var params = {};
	
	if (email_field) {
		params['email'] = $ev(email_field);
	}
	if (login_field) {
		params['login'] = $ev(login_field);
	}
	if (display_name_field) {
		params['display_name'] = $ev(display_name_field);
	}
	if (p1) {
		params['new_password'] = p1;
	}
	
	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: params,
		success: function(response, opts) {
			var json = Ext.decode(response.responseText);
			Pyrone.notify($e('eid-notify'), tr('YOUR_PROFILE_HAS_BEEN_UPDATED'));
		},
		failure: function() {
			alert(tr('AJAX_REQUEST_ERROR'));
		}
	});
};

