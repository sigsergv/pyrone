<%inherit file="/admin/base.mako"/>

<%def name="title()">${_('Backups')}</%def>

<h2>${_('Backups management')}</h2>

<div class="warning" style="display: none;" id="eid-error"></div>

<h3>${_('Backup archives')} 
<!--<a href="#" class="border-icon">${_('Upload backup file')}</a>--> 
<a href="#" class="border-icon" onclick="Pyrone.backup.backupNow('${url('admin_backup_now')}'); return false;">Backup blog now</a></h3>

<table border="0" class="items-list" cellpadding="0" cellspacing="0" id="backups-table">
<tr>
  <th><input type="checkbox" onclick="selectDeselectAll(this);" id="select-all-files-cb" title="${_('Select/deselect all files')}"/></th>
  <th></th>
  <th>${_('Backup filename')}</th>
  <th>${_('File size')}</th>
</tr>

% for b in backups:
<tr id="list-tr-${b['id']}">
  <td><input type="checkbox" value="${b['id']}" class="list-cb"/></td>
  <td><a href="#" class="border-icon" onclick="Pyrone.backup.startRestoreReq('${url('admin_restore_backup', backup_id=b['id'])}', 'rb-${b['id']}'); return false;" id="rb-${b['id']}">${_('restore')}</a></td>
  <td><a href="${url('admin_download_backup', backup_id=b['id'])}" title="${_('Download backup')}">${b['filename']}</a></td>
  <td><span title="${_('%i bytes') % b['size']}">${h.hsize(b['size'])}</span></td>
</tr>
% endfor
</table>

<div>
    <a href="#" class="border-icon" onclick="Pyrone.backup.listDeleteSelectedReq('backups-table', '${url('admin_delete_backups_ajax')}'); return false;" id="delete-selected-btn">${_('delete selected')}</a>
</div>