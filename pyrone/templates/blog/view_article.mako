<%inherit file="/blog/base.mako"/>\
<%namespace file="/widgets/comment.mako" name="cm"/>

<%
    editor_permission = h.auth.has_permission('edit_article') 
    admin_permission = h.auth.has_permission('admin') 
    authenticated = h.auth.get_user()
%>
<%def name="title()">\
${c.article.title}
</%def>


<div class="notify" style="display:none;" id="notify-block"></div>

<div class="article">
  <div class="title">${c.article.title}\
% if c.article.is_draft:
 <span class="warning">${_('draft')}</span>\
%endif
% if editor_permission:
 <a href="${h.url(controller='blog', action='edit_article', article_id=c.article.id)}" class="border-icon">${_('edit')}</a>\
 <a href="#" onclick="Pyrone.article.deleteArticleReq('${h.url(controller='blog', action='delete_article_ajax',\
 article_id=c.article.id)}', '${c.article.id}'); return false;" class="border-icon" id="ad-${c.article.id}">${_('delete')}</a>\
%endif
  </div>
  
  <div class="date">${h.timestamp_to_str(c.article.published)}</div>
% if len(c.article.tags):
  <div class="tags">${_('Tags:')} ${h.article_tags_links(c.article)|n}</div>
% endif
  <div class="body">${c.article.rendered_body|n}</div>
</div>

<h4>${_('Comments')}</h4>

<div class="article-comments">
  <!-- comments here -->
% for comment in c.comments:
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
  <div><input type="button" value="${_('save')}" onclick="Pyrone.article.submitEditCommentForm('${h.url(controller='blog', action='edit_comment_ajax', comment_id='666')}');"/> 
    <a href="#" onclick="Pyrone.article.cancelEditCommentForm(); return false;">${_('close')}</a>
  </div>
  
  </form>
  </div>
% endif

% if c.article.is_commentable:
  
  <!-- new comment form here -->
  <div class="article-new-comment" id="c--1">
    <a name="leave-comment"></a>
    <a href="#" id="eid-leave-comment-link-bottom" style="display:none;" onclick="Pyrone.article.replyToComment(-1); return false;">${_('leave comment')}</a>
    <form action="${h.url(controller='blog', action='add_article_comment', article_id=c.article.id)}" method="POST" id="eid-comment-form">
      <input type="hidden" id="fid-parent-comment" value=""/>
      <input type="hidden" id="fid-article_id" value="${c.signature}"/>
      <dl class="form">
        <dd><div id="eid-comment-error" style="display: none;" class="error"></div></dd>
        <dd><div id="eid-comment-notify" style="display: none;" class="notify"></div></dd>
        <dt>${_(u'Comment text (<a class="new-window" target="_blank" href="/comment-markup-tip-en.html" title="Open in new window">Markdown</a> is allowed).')|n}
        % if authenticated is None:
        ${_(u'<strong>Anonymous visitors, please pay attention that comments with more than one hyperlink (including field “website”) will be put on moderation. Sign in to post without such limitations.</strong>')|n}
        % endif
        </dt>
        <dd><textarea name="body" class="small" id="fid-comment-body"></textarea></dd>
% if authenticated is not None:
        ${h.form_checkbox('is_subscribed', None, c.is_subscribed, dict(), None, _('Subscribe to answers'))|n}
        <dd>${h.user_link(authenticated)|n}</dd>
        <input type="hidden" id="fid-comment-displayname" value=""/>
        <input type="hidden" id="fid-comment-email" value=""/>
        <input type="hidden" id="fid-comment-website" value=""/>
%else:
        <dt>${_('Your name (required, 50 characters or less)')}</dt>
        <dd><input type="text" id="fid-comment-displayname" value="${c.comment_display_name}"/></dd>
      
        <dt>${_("Your email (won't be published, required if you want to receive answers)")}</dt>
        <dd><input type="text" id="fid-comment-email" value="${c.comment_email}"/></dd>
        ${h.form_checkbox('is_subscribed', None, c.is_subscribed, dict(), None, _('Subscribe to answers'))|n}
      
        <dt>${_('Your website')}</dt>
        <dd><input type="text" id="fid-comment-website" value="${c.comment_website}"/></dd>
%endif
        <dd><input type="button" value="${_('post comment')}" onclick="Pyrone.article.postComment();"></dd>
      </dl>
    </form>
  </div>
% else:
  <div>${_('commenting is disabled')}</div>
% endif
</div>