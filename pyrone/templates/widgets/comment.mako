<%def name="render(comment, admin_permission)">
    <a name="comment-${comment.id}"></a>
    <div class="title">
    % if comment.user is not None:
    ${h.user_link(comment.user)|n}
    % else:
    <span class="name">${comment.display_name}</span>
    % endif
    | <span class="date">${h.timestamp_to_str(comment.published, _('DATE_TIME_SHORT'))}</span>
    % if admin_permission:
    | ${_('IP address:')} <span class="name comment-ip-address">${comment.ip_address}</span>
      % if comment.xff_ip_address is not None:
        (${_('X-Forwarded-For')} <span class="name comment-ip-address">${comment.xff_ip_address}</span>)
      %endif 
    | ${_('Email:')} <span class="name comment-email">${h.cond(comment._real_email is None, u'∅', comment._real_email)}</span>
    %endif 
    </div>
    <div class="body">${comment.rendered_body|n}</div>
    <div class="links"><a href="#" onclick="Pyrone.article.replyToComment('${comment.id}'); return false;">${_('reply to this comment')}</a>\
    <a href="#comment-${comment.id}">${_('link')}</a>
    % if admin_permission:
      % if not comment.is_approved:
      <a href="#" onclick="Pyrone.article.approveComment('${url('blog_approve_comment_ajax', comment_id=comment.id)}', '${comment.id}'); return false;" id="ca-${comment.id}" class="border-icon">${_('approve')}</a>
      % endif
      <a href="#" onclick="Pyrone.article.deleteCommentReq('${url('blog_delete_comment_ajax', comment_id=comment.id)}', '${comment.id}'); return false;" id="cd-${comment.id}" class="border-icon">${_('delete')}</a>
      <a href="#" onclick="Pyrone.article.showEditCommentForm('${url('blog_edit_comment_ajax', comment_id=comment.id)}', '${url('blog_edit_comment_fetch_ajax', comment_id=comment.id)}', '${comment.id}'); return false;" class="border-icon">${_('edit')}</a>
    % endif
    </div>
</%def>