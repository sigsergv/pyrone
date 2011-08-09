## -*- coding: utf-8 -*-
<%inherit file="/blog/base.mako"/>\

<%def name="title()">${_('My profile')}</%def>

<div class="notify" style="display:none;" id="eid-notify"></div>

<form id="my-profile-properties" onsubmit="Pyrone.account.saveMyProfile('${h.url(controller='account', action='save_my_profile_ajax')}'); return false;">
  <dl class="form">
% if c.user.kind == 'local':
  ${h.form_input_text('login', _('Login name'), c.user.login, dict())|n}
  ${h.form_input_text('display_name', _('Display name'), c.user.display_name, dict())|n}
  ${h.form_input_text('password_1', _('Password'), '', dict())|n}
  ${h.form_input_text('password_2', _(u'…and repeat password'), '', dict())|n}
% elif c.user.kind == 'twitter':
% endif
  ${h.form_input_text('email', _('Email address'), c.user.email, dict())|n}
  
  <dd style="padding-top: 8px;"><input type="submit" value="${_('save')}"/></dd>
  </dl>
</form>

