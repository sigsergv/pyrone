<%inherit file="/blog/base.mako"/>\
<%namespace file="/widgets/comment.mako" name="cm"/>
<%
	authenticated = user.kind != 'anonymous'
	editor_permission = user.has_permission('edit_article') 
	admin_permission = user.has_permission('admin') 
%>
<%def name="title()">\
${article.title}
</%def>

<script language="javascript">
Ext.onReady(function() {
	// scroll to needed position
	var hash = window.location.hash, 
		comment_id = -1;
		
	// extract comment id
	if (/#comment-([0-9]+)$/.test(hash)) {
		comment_id = RegExp.$1;
	} else {
		return;
	}
	
	var cb = $e('c-'+comment_id);
	if (cb) {
		cb.addClass('active');
	}
});
</script>

<div class="notify" style="display:none;" id="notify-block"></div>

<div class="article">
  <div class="title">${article.title}\
% if article.is_draft:
 <span class="warning">${_('draft')}</span>\
%endif
% if editor_permission:
 <a href="${url('blog_edit_article', article_id=article.id)}" class="border-icon">${_('edit')}</a>\
 <a href="#" onclick="Pyrone.article.deleteArticleReq('${url('blog_article_delete_ajax', article_id=article.id)}', '${article.id}'); return false;" class="border-icon" id="ad-${article.id}">${_('delete')}</a>\
%endif
  </div>
  
  <div class="date">${h.timestamp_to_str(article.published)}</div>
% if len(article.tags):
  <div class="tags">${_('Tags:')} ${h.article_tags_links(request, article)|n}</div>
% endif
  <div class="body">${article.rendered_body|n}</div>
</div>

<h4><a name="comments"></a>${_('Comments')}</h4>

<div class="article-comments">
  <!-- comments here -->
% for comment in comments:
  <div class="article-comment${h.cond(comment.is_approved, '', ' not-approved')}" id="c-${comment.id}" style="margin-left: ${50*comment._indent}px">
    <div id="c-inner-${comment.id}">
    ${cm.render(comment, admin_permission)}
    </div>
  </div>
% endfor

% if admin_permission:
  <!-- edit comment form here -->
  <div class="article-inline-comment-edit" id="c-edit" style="display: none;">
  <form>
  <input type="hidden" id="c-edit-comment_id"/>
  <div> <input type="text" id="c-edit-name" class="display-name" title="${_('Display name of the visitor')}"/> 
    <input type="text" id="c-edit-date" title="${_('Comment date and time')}" class="date"/>
    <label><input id="c-edit-is_subscribed" type="checkbox"/>${_('subscribed')}</label>
  </div> 
  <div> <input type="text" id="c-edit-email" class="display-name" title="${_('Email address of the visitor')}">
    <input type="text" id="c-edit-ip" title="${_('Visitor ip address')}" class="ip"/>
    <input type="text" id="c-edit-xffip" title="${_('Visitor X-Forwarded-For address')}" class="ip"/> 
    <input type="text" id="c-edit-website" title="${_('Visitor website')}" class="display-name"/> 
  </div>
  
  <div><textarea id="c-edit-body" class="body"></textarea></div>
  <div><input type="button" value="${_('save')}" onclick="Pyrone.article.submitEditCommentForm('${url('blog_edit_comment_ajax', comment_id='666')}');"/> 
    <a href="#" onclick="Pyrone.article.cancelEditCommentForm(); return false;">${_('close')}</a>
  </div>
  
  </form>
  </div>
% endif

% if article.is_commentable:
  
  <!-- new comment form here -->
  <div class="article-new-comment" id="c--1">
    <a name="leave-comment"></a>
    <a href="#" id="eid-leave-comment-link-bottom" style="display:none;" onclick="Pyrone.article.replyToComment(-1); return false;">${_('leave comment')}</a>
    <form action="${url('blog_add_article_comment', article_id=article.id)}" method="POST" id="eid-comment-form">
      <input type="hidden" id="fid-parent-comment" value=""/>
      <input type="hidden" id="fid-article_id" value="${signature}"/>
      <dl class="form">
        <dd><div id="eid-comment-error" style="display: none;" class="error"></div></dd>
        <dd><div id="eid-comment-notify" style="display: none;" class="notify"></div></dd>
        <dt>${_(u'Comment text (<a class="new-window" target="_blank" href="/static/comment-markup-tip-en.html" title="Open in new window">Markdown</a> is allowed).')|n}
        % if authenticated is None:
        ${_(u'<strong>Anonymous visitors, please pay attention that comments with more than one hyperlink (including field “website”) will be put on moderation. Sign in to post without such limitations.</strong>')|n}
        % endif
        </dt>
        <dd><textarea name="body" class="small" id="fid-comment-body"></textarea></dd>
% if authenticated:
        ${h.form_checkbox('is_subscribed', None, is_subscribed, dict(), None, _('Subscribe to answers'))|n}
        <dd>${h.user_link(user)|n}</dd>
        <input type="hidden" id="fid-comment-displayname" value=""/>
        <input type="hidden" id="fid-comment-email" value=""/>
        <input type="hidden" id="fid-comment-website" value=""/>
%else:
        <dt>${_('Your name (required, 50 characters or less)')}</dt>
        <dd><input type="text" id="fid-comment-displayname" value="${comment_display_name}"/></dd>
      
        <dt>${_("Your email (won't be published, required if you want to receive answers)")}</dt>
        <dd><input type="text" id="fid-comment-email" value="${comment_email}"/></dd>
        ${h.form_checkbox('is_subscribed', None, is_subscribed, dict(), None, _('Subscribe to answers'))|n}
      
        <dt>${_('Your website')}</dt>
        <dd><input type="text" id="fid-comment-website" value="${comment_website}"/></dd>
%endif
        <dd><input type="button" value="${_('post comment')}" onclick="Pyrone.article.postComment();"></dd>
      </dl>
    </form>
  </div>
% else:
  <div>${_('commenting is disabled')}</div>
% endif
</div>
