<%inherit file="/admin/base.mako"/>

<%def name="title()">${_("Visitors' emails")}</%def>

<h2>${_("Visitors' emails")}</h2>

<script language="javascript">
function changeEmailVerified(cb)
{
	var url = '${url('admin_visitor_email_edit_ajax')}';
	Pyrone.account.changeEmailVerified(cb.value, cb.checked, url);
} 
</script>
<table border="0" class="items-list" cellpadding="0" cellspacing="0" id="emails-table">
<tr>
    <th><input type="checkbox" onclick="selectDeselectAll(this);" id="select-all-emails-cb" title="${_('Select/deselect all files')}"/></th>
    <th>${_('E-mail')}</th>
    <th>${_('Verified')}</th>
</tr>

% for email in emails:
<tr id="list-tr-${email.id}">
    <td><input type="checkbox" value="${email.id}" class="list-cb"/></td>
    <td>${email.email}</td>
    <td align="center"><input type="checkbox" value="${email.id}"${h.cond(email.is_verified, 'checked="checkd"', '')} onclick="changeEmailVerified(this);"/></td>
</tr>
% endfor

</table>

<div>
    <a href="#" class="border-icon" onclick="Pyrone.file.listDeleteSelectedReq('emails-table', '${url('admin_visitors_emails_delete_ajax')}'); return false;" id="delete-selected-btn">${_('delete selected')}</a>
</div>