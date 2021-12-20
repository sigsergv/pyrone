<%
    admin_permission = user is not None and user.has_role('admin')
%>
<div class="widget">
<div class="section">${_('Pinned posts')} 
% if admin_permission:
<a href="${url('admin_settings_widget_pages')}" title="${_('edit')}"><span class="fa fa-pencil"></span></a>
%endif
<ul>
% for link in h.get_pages_widget_links(request):
  <li><a href="${link['url']}">${link['title']}</a></li>
% endfor
</ul>
</div>
</div>