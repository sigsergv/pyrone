<%
  search_code = h.get_config(request, 'site_search_widget_code')
%>
% if search_code is not None and search_code != '':
<div class="widget widget-search">
  <div class="section">${_('Search blog')}</div>
  ${search_code|n}
</div>
% endif

