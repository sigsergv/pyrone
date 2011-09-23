<%
    admin_permission = user.has_permission('admin')
    lang = h.lang.lang(request)
%>
<div class="widget">
<div class="section">${_('Pages')} 
% if admin_permission:
<a href="${url('admin_settings_widget_pages')}" class="border-icon">${_('edit')}</a>
%endif
<ul>
% for link in h.get_pages_widget_links(lang):
  <li><a href="${link['url']}">${link['title']}</a></li>
% endfor
</ul>
</div>
</div>