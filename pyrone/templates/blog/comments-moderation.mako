<%inherit file="/blog/base.mako"/>

<%def name="title()">${_('Comments moderation')}</%def>

<h2>${_('Comments moderation')}</h2>

<div class="comments-moderation-queue">

% for comment in comments:
<div class="comment" id="c-${comment.id}">
  <div class="title">
  % if comment.user is not None:
  <span class="name">${h.user_link(comment.user)|n}</span>
  % else:
  <span class="name">${comment.display_name}</span>
  % endif
  | <span class="name comment-email">${_('E-mail')}: ${h.cond(comment._real_email is None, u'∅', comment._real_email)}</span>
  | <span class="name">${_('Visitor website')}: ${h.cond(comment.website, comment.website, u'∅')}</span>
  | ${_('IP address:')} <span class="name comment-ip-address">${comment.ip_address}</span>
      % if comment.xff_ip_address is not None:
        (${_('X-Forwarded-For')} <span class="name comment-ip-address">${comment.xff_ip_address}</span>)
      %endif 
  | <a href="${h.article_url(request, comment.article)}#comment-${comment.id}">${_('link')}</a>
  </div>
  
  <div class="links">
	  <a href="#" onclick="Pyrone.article.approveModeratedComment('${url('blog_approve_comment_ajax', comment_id=comment.id)}', '${comment.id}'); return false;" id="ca-${comment.id}" class="border-icon">${_('approve')}</a>
	  <a href="#" onclick="Pyrone.article.deleteModeratedCommentReq('${url('blog_delete_comment_ajax', comment_id=comment.id)}', '${comment.id}'); return false;" id="cd-${comment.id}" class="border-icon">${_('delete')}</a>
  </div>
  
  % if comment._truncated_body is not None:
	  <div class="body" id="c-c-${comment.id}"><p>${comment._truncated_body} <a href="#" onclick="Pyrone.article.expandModeratedComment('${comment.id}'); return false;">${_(u'expand…')}</a></p></div>
	  <div class="body" id="c-e-${comment.id}" style="display: none;">${comment.rendered_body|n}</div>
  % else:
  	<div class="body">${comment.rendered_body|n}</div>
  % endif
</div>
% endfor
</div>