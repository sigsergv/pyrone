<%
    authenticated = h.auth.get_user()
%>
<%inherit file="/admin/base.mako"/>

<%def name="title()">${_('Accounts')}</%def>

<h2>${_('User accounts')}</h2>

<table border="0" class="items-list" cellpadding="0" cellspacing="0" id="accounts-table">
<tr>
  <th><input type="checkbox" onclick="selectDeselectAll(this);" id="select-all-users-cb" title="${_('Select/deselect all users')}"/></th>
  <th>${_('User')}</th>
  <th>${_('Display name')}</th>
  <th>${_('Email')}</th>
  <th>${_('Information')}</th>
</tr>

% for user in c.users:
<tr>
  <td><input type="checkbox" class="user-cb" value="${user.id}" ${h.cond(authenticated.id==user.id, ' disabled="disabled" \
  title="'+_('You cannot delete current user')+'"', '')|n} /></td>
  <td>${h.user_link(user)|n}</td>
  <td>${user.display_name or '-'}</td>
  <td>${user.email or '-'}</td>
  <td>${h.cond(user.has_permission('admin'), h.span_info(_('admin')), '')|n}</td>
</tr>
% endfor
</table>

<div>
    <a href="#" class="border-icon" onclick="Pyrone.account.listDeleteSelectedReq('accounts-table', '${h.url(controller='admin', action='delete_accounts')}'); return false;" id="delete-selected-btn">${_('delete selected')}</a>
</div>