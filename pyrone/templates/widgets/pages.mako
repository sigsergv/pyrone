<%
    admin_permission = user.has_role('admin')
%>
<div class="widget">
<div class="section">${_('Pages')} 
% if admin_permission:
<a href="${url('admin_settings_widget_pages')}" title="${_('edit')}"><span class="fa fa-pencil"></span></a>
%endif
<ul>
% for link in h.get_pages_widget_links():
  <li><a href="${link['url']}">${link['title']}</a></li>
% endfor
</ul>
</div>
</div>