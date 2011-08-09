<div class="widget">
<div class="section">${_('Tags cloud')}</div>
% for t in h.g.get_public_tags_cloud():
  <a href="${h.url(controller='blog', action='tag_articles', tag=t[0])}" class='tag-${t[1]}'>${t[0]}</a>
% endfor
</div>