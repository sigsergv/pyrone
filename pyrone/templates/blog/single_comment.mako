<%
    admin_permission = h.auth.has_permission('admin') 
%>\
<%namespace file="/widgets/comment.mako" name="cm"/>\
${cm.render(c.comment, admin_permission)|n}
