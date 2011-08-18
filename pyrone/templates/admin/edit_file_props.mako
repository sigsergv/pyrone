<%inherit file="/admin/base.mako"/>

<%def name="title()">${_('Edit file properties')}</%def>

<h2>${_('Edit file properties')}</h2>

<form action="${url('admin_edit_file_props', file_id=file.id)}" id="upload-form"\
  method="post" onsubmit="return Pyrone.file.checkUploadForm('${url('admin_edit_file_props_check_ajax', file_id=file.id)}','upload-form');"\
  enctype="multipart/form-data">
  <dl class="form">
    ${h.form_input_text('filename', _('Name of the file'), file.name, errors)|n}
    
    ${h.form_selector('dltype', _('File access type'), 
    [ ( 'download', _('display file download dialog (suitable for documents, archives)')), \
    ('auto', _('leave processing to web browser (suitable for pictures)'))], \
    file.dltype, errors,\
    help=_('What should happen when user open URL to the file in web browser') )|n}
    
    ${h.form_input_text('content_type', _('File content type'), file.content_type, errors)|n}
    
    <dd style="padding-top: 8px;"><input type="submit" value="${_('submit')}"/></dd>
  </dl>
  
</form>

