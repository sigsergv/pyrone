<%inherit file="/blog/base.mako"/>

<%def name="title()">${_('My profile')}</%def>

<div class="notify" style="display:none;" id="eid-notify"></div>

<form id="my-profile-properties" onsubmit="Pyrone_account_saveMyProfile('${url('account_save_my_profile_ajax')}'); return false;">
  <dl class="form">
% if user.kind == 'local':
  ${h.form_input_text('login', _('Login name'), user.login, {})|n}
  ${h.form_input_text('display_name', _('Display name'), user.display_name, {})|n}
  ${h.form_input_text('password_1', _('Password'), '', {})|n}
  ${h.form_input_text('password_2', _(u'…and repeat password'), '', {})|n}
% elif user.kind == 'twitter':
  <div>${_('You are signed in using twitter account {0}.').format(h.user_link(user))|n}</div>
% endif
  ${h.form_input_text('email', _('Email address (for notifications)'), user.email, {})|n}
  
  <dd style="padding-top: 8px;">
    <button class="button" onclick="$('#my-profile-properties').submit(); return false;"><span class="fa fa-save"></span> ${_('save')}</button>
  </dd>
  </dl>
</form>

