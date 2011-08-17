<%inherit file="/admin/base.mako"/>

<%def name="title()">${_('Blog settings')}</%def>

<h2>${_('Blog settings')}</h2>

<div class="notify" style="display:none;" id="eid-notify"></div>
<form action="/" onsubmit="Pyrone.settings.saveSettings('${h.url(controller='admin', action='settings_save_ajax')}'); return false;">
<dl class="form">
  <dd style="padding-top: 8px;"><input type="submit" value="${_('save')}"/></dd>
  
  <h3>${_('General')}</h3>
  ${h.form_input_text('site_title', _('Blog title'), c.settings['site_title'], c.errors)|n}
  ${h.form_input_text('site_base_url', _('Base blog address'), c.settings['site_base_url'], c.errors,\
    help=_('URL that will be used in all external communications (notification messages for example)'))|n}
  ${h.form_input_text('site_copyright', _('Copyright string'), c.settings['site_copyright'], c.errors,\
    help=_(u'A string displayed at the bottom of each blog page, just before “Powered by Pyrone”'))|n}
  ${h.form_input_text('elements_on_page', _('Number of elements on a page'), c.settings['elements_on_page'], c.errors,\
    help=_(u'How much elements (articles etc) display on single page'))|n}
  ${h.form_input_text('site_style', _('Blog style (skin)'), c.settings['site_style'], c.errors)|n}
  ${h.form_input_text('image_preview_width', _('Picture preview width'), c.settings['image_preview_width'], c.errors,\
    help=_(u'Width of automatically generated preview to be used as smaller copy of original picture.'))|n}
  
  <h3>${_('Twitter Auth')}</h3>
  <dt><strong>${_('To use Twitter authentication you MUST <a href="https://dev.twitter.com/apps">register</a> a new twitter application and obtain consumer key and secret.')|n}</strong></dt>
  ${h.form_input_text('tw_consumer_key', _('Consumer key'), c.settings['tw_consumer_key'], c.errors)|n}
  ${h.form_input_text('tw_consumer_secret', _('Consumer secret'), c.settings['tw_consumer_secret'], c.errors)|n}
  
  <h3>${_('Notifications')}</h3>
  ${h.form_input_text('admin_notifications_email', _('Email address for system notifications'), c.settings['admin_notifications_email'], c.errors,
    help=_('Email address for the system notification: user added, comment added for moderation etc'))|n}
  
  <dt>${_('Select notifications you want to receive')}</dt>
  ${h.form_checkbox('admin_notify_new_comments', None, c.settings['admin_notify_new_comments'], c.errors, 
  	label=_('new comment added (including comment moderation requests)'))|n}
  ${h.form_checkbox('admin_notify_new_user', None, c.settings['admin_notify_new_user'], c.errors, 
  	label=_('new user registered'))|n}
  ${h.form_input_text('verification_msg_sibject_tpl', _('Email address verification message subject template'), c.settings['verification_msg_sibject_tpl'],
    c.errors, help=_('Plain text, no HTML, allowed substitution symbols: {vrf_link}, {email}'))|n}
  ${h.form_textarea('verification_msg_body_tpl', _('Email address verification message body template'), c.settings['verification_msg_body_tpl'],
    c.errors, help=_('Plain text, no HTML, allowed substitution symbols: {vrf_link}, {email}'), height=200)|n}
  ${h.form_input_text('comment_answer_msg_subject_tpl', _('Answer to comment notification message subject template'), c.settings['comment_answer_msg_subject_tpl'],
    c.errors, help=_('Plain text, no HTML, allowed substitution symbols: {site_title}, {visitor}, {comment_title}, {answer_title}, {email}'))|n}
  ${h.form_textarea('comment_answer_msg_body_tpl', _('Answer to comment notification message body template'), c.settings['comment_answer_msg_body_tpl'],
    c.errors, help=_('Plain text, no HTML, allowed substitution symbols: {site_title}, {visitor}, {comment_title}, {comment_body}, {answer_title}, {answer_body}, {email}'), height=200)|n}
    
  <dd style="padding-top: 8px;"><input type="submit" value="${_('save')}"/></dd>
    
</dl>
</form>