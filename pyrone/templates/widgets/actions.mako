<%
    authenticated = h.auth.get_user() is not None
    writer_permission = h.auth.has_permission('write_article')
    editor_permission = h.auth.has_permission('edit_article')
    admin_permission = h.auth.has_permission('admin')
%>
% if authenticated:

<div class="widget">
  <div class="section">${_('Actions')}</div>
% if writer_permission:
  <div><a href="${h.url(controller='blog', action='write_article')}">${_('Write new article')}</a></div>
% endif
% if admin_permission:
  <div><a href="${h.url(controller='admin', action='settings')}">${_('Settings')}</a></div>
  <div><a href="${h.url(controller='admin', action='list_accounts')}">${_('Accounts')}</a></div>
  <div><a href="${h.url(controller='admin', action='list_files')}">${_('Manage files')}</a></div>
  <div><a href="${h.url(controller='admin', action='list_backups')}">${_('Backup/restore')}</a></div>
% endif
</div>
% endif