<%inherit file="/admin/base.mako"/>

<%def name="title()">${_('Files')}</%def>

<h2>${_('Files management')}</h2>

<div id="upload-file-form" style="display:none" class="inline-form">
<form action="${url('admin_upload_file')}" id="upload-form"\
  method="post" onsubmit="return Pyrone.file.checkUploadForm('${url('admin_upload_file_check_ajax')}','upload-form');"\
  enctype="multipart/form-data">
  <dl class="form">
    <dt>${_('Choose file to upload"')}</dt>
    <dd><input type="file" id="fid-filedata" onchange="Pyrone.file.uploadFormFileSelected()" name="filedata" onchange="fileSelected(this);"/> \
    <span class="hint">${_(u'← First choose file (other fields will be filled automatically)')}</span></dd>
    
    ${h.form_input_text('filename', _('Name of the file (required, case-sensitive)'), '', dict(),\
    help=_('File will be accessed using specified name'))|n}
    
    ${h.form_selector('dltype', _('File access type'), 
    [ ( 'download', _('display file download dialog (suitable for documents, archives)')), \
    ('auto', _('leave processing to web browser (suitable for pictures)'))], \
    'auto', dict(),\
    help=_('What should happen when user open URL to the file in web browser') )|n}
    
    <dd style="padding-top: 8px;"><input type="submit" value="${_('upload')}"/> <a href="#" onclick="$hide('upload-file-form'); $show('show-upload-form-link'); return false;">${_('cancel')}</a></dd>
  </dl>
  
</form>
</div>

<div><a href="#" id="show-upload-form-link" onclick="$show('upload-file-form'); $hide('show-upload-form-link'); return false;">${_('upload new file')}</a></div>

<table border="0" class="items-list" cellpadding="0" cellspacing="0" id="files-table">
<tr>
    <th><input type="checkbox" onclick="selectDeselectAll(this);" id="select-all-files-cb" title="${_('Select/deselect all files')}"/></th>
    <th></th>
    <th>${_('Filename')}</th>
    <th>${_('Content type')}</th>
    <th>${_('File size')}</th>
</tr>

% for f in files:
<tr id="list-tr-${f.id}">
  <td><input type="checkbox" value="${f.id}" class="list-cb"/></td>
  <td><a href="${url('admin_edit_file_props', file_id=f.id)}" class="border-icon"/>${_('edit')}</a>
  </td>
  <td><a href="${url('blog_download_file', filename=f.name)}" title="${_('file URL')}">${f.name}</a></td>
  <td>${f.content_type}</td> 
  <td><acronym title="${_('%i bytes') % f.size}">${h.hsize(f.size)}</td>
</tr>
% endfor
</table>

<div>
    <a href="#" class="border-icon" onclick="Pyrone.file.listDeleteSelectedReq('files-table', '${url('admin_delete_files_ajax')}'); return false;" id="delete-selected-btn">${_('delete selected')}</a>
</div>