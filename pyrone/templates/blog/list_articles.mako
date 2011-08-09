<%inherit file="/blog/base.mako"/>\
<%
    editor_permission = h.auth.has_permission('edit_article') 
    admin_permission = h.auth.has_permission('admin')
%>

<%def name="title()">${c.title}</%def>

<%def name="preview(article)">
<%
  article_url = h.url(controller='blog', action='view_article',\
  shortcut=article.shortcut, shortcut_date=article.shortcut_date)
%>
	<div class="article-preview">
<div class="title"><a href="${article_url}">${article.title}</a>\
% if article.is_draft:
 <span class="warning">${_('draft')}</span>\
%endif
% if editor_permission:
 <a href="${h.url(controller='blog', action='edit_article', article_id=article.id)}" class="border-icon">${_('edit')}</a>\
 <a href="#" onclick="Pyrone.article.deleteArticleReq('${h.url(controller='blog', action='delete_article_ajax', \
 article_id=article.id)}', '${article.id}'); return false;" class="border-icon" id="ad-${article.id}">${_('delete')}</a>\
%endif
  </div>
  <div class="date">${_('Posted by %(author)s on %(date)s') % dict(author=article.user.display_name, date=h.timestamp_to_str(article.published))}</div>
  <div class="before-preview"></div>
  <div class="preview">${article.get_html_preview()|n}</div>
  <div class="after-preview"></div>
%if article.is_splitted:
  <div class="splitter"><a href="${article_url}">${_('continue reading')}</a></div>
%endif
  <div class="tags">${_('Tags:')} ${h.article_tags_links(article)|n}</div>
<div class="footer"> 
${_('Comments:')} ${article.comments_approved}
% if admin_permission:
/ ${_('not approved comments:')} <span class="hint">${h.cond(article.comments_total-article.comments_approved == 0, '0', article.comments_total-article.comments_approved)}</span>
% endif
</div>
</div>
</%def>

% if len(c.articles):
  % for a in c.articles:
  	${preview(a)}
  % endfor
% else:
${_('No articles here.')}
% endif

## display pager
<div class="pager">
${h.cond(c.next_page is not None, '<a href="%s">%s</a>' % (c.next_page, _(u'←newer')), _(u'←newer'))|n} 
${h.cond(c.prev_page is not None, '<a href="%s">%s</a>' % (c.prev_page, _(u'older→')), _(u'older→'))|n} 

</div>