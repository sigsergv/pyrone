<%
    authenticated = request.user.kind != 'anonymous'
    
    writer_permission = user.has_role('writer')
    editor_permission = user.has_role('editor')
    admin_permission = user.has_role('admin')
%>
% if authenticated:

<div class="widget widget-actions">
  <div class="section">${_('Actions')}</div>
% if writer_permission:
  <div class="action-item"><a href="${url('blog_write_article')}">${_('Write new article')}</a></div>
% endif
% if admin_permission:
  <div class="action-item"><a href="${url('blog_view_moderation_queue')}">${_('Not approved comments')} (${h.get_not_approved_comments_count()})</a></div>
  <div class="action-item"><a href="${url('admin_list_accounts')}">${_('Accounts')}</a></div>
  <div class="action-item">↳ <a href="${url('admin_list_visitors_emails')}">${_("Visitors' emails")}</div>
  <div class="action-item"><a href="${url('admin_list_files')}">${_('Manage files')}</a></div>
  <div class="action-item"><a href="${url('admin_list_backups')}">${_('Backup/restore')}</a></div>
  <div class="action-item"><a href="${url('admin_settings')}">${_('Settings')}</a></div>
% endif
</div>
% endif
