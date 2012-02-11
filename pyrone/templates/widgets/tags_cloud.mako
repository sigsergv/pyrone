<div class="widget">
<div class="section"><!--${_('Tags cloud')}--></div>
% for t in h.get_public_tags_cloud():
  <a href="${url('blog_tag_articles', tag=t[0])}" class='tag-${t[1]}'>${t[0]}</a>
% endfor
</div>
