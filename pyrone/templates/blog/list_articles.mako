<%inherit file="/blog/base.mako"/>\
<%
    editor_permission = user.has_permission('edit_article') 
    admin_permission = user.has_permission('admin')
%>


<%def name="title()">${page_title}</%def>

<%def name="preview(article)">
<%
  article_url = h.article_url(request, article)
%>
	<div class="article-preview">
<div class="title"><a href="${article_url}">${article.title}</a>\
% if article.is_draft:
 <span class="warning">${_('draft')}</span>\
%endif
% if editor_permission:
 <a href="${url('blog_edit_article', article_id=article.id)}" class="border-icon">${_('edit')}</a>\
 <a href="#" onclick="Pyrone.article.deleteArticleReq('${url('blog_article_delete_ajax', article_id=article.id)}',\
 '${article.id}'); return false;" class="border-icon" id="ad-${article.id}">${_('delete')}</a>\
%endif
  </div>
  <div class="date">${_('Posted by %(author)s on %(date)s') % dict(author=article.user.display_name, date=h.timestamp_to_str(article.published, _('DATE_TIME_SHORT')))}</div>
  <div class="before-preview"></div>
  <div class="preview">${article.get_html_preview()|n}</div>
  <div class="after-preview"></div>
%if article.is_splitted:
  <div class="splitter"><a href="${article_url}">${_('continue reading')}</a></div>
%endif
  <div class="tags">${_('Tags:')} ${h.article_tags_links(request, article)|n}</div>
<div class="footer">

% if article.comments_approved > 0:
<a href="${article_url}#comments">${_('Comments:')} ${article.comments_approved}</a>
% else:
${_('Comments:')} 0
% endif
% if admin_permission:
/ ${_('not approved comments:')} <span class="hint">${h.cond(article.comments_total-article.comments_approved == 0, '0', article.comments_total-article.comments_approved)}</span>
% endif
</div>
</div>
<div class="article-preview-after"></div>
</%def>

% if len(articles):
  % for a in articles:
  	${preview(a)}
  % endfor
% else:
${_('No articles here.')}
% endif

## display pager
<div class="pager">
${h.cond(next_page is not None, '<a href="%s">%s</a>' % (next_page, _(u'←newer')), _(u'←newer'))|n} 
${h.cond(prev_page is not None, '<a href="%s">%s</a>' % (prev_page, _(u'older→')), _(u'older→'))|n} 

</div>
