<%
    admin_permission = user.has_role('admin') 
%>\
<%namespace file="/widgets/comment.mako" name="cm"/>\
${cm.render(comment, admin_permission)|n}
