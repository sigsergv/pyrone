<%inherit file="/admin/base.mako"/>

<%def name="title()">${_(u'Widget “Pages” parameters')}</%def>

<h2>${_(u'Widget “Pages” parameters')}</h2>
<div class="notify" style="display:none;" id="eid-notify"></div>

<!-- render table, up/down buttons -->

<form action="/" onsubmit="Pyrone.settings.widgets.pagesSave('${url('admin_settings_widget_pages_save_ajax')}'); return false;">
<dl class="form">
  ${h.form_textarea('widget_pages_pages_spec', _('Pages list'), 
  	settings['widget_pages_pages_spec'], errors, \
  	help=_(u'One site definition per line, empty lines are ignored. Incorrect lines are ignored.'), height=200)|n}
  	
  <dd>${_('Every line defines one site, site definition line format is the following: '+\
  '<code><strong>delim</strong><em>language</em><strong>delim</strong><em>URL</em><strong>delim</strong><em>link description</em></code>')|n}</dd>
  <dd>${_(u'You may use any character as <strong>delim</strong>, e.g. pipe “|” or exclamation mark “!”.')|n}</dd>


  <dd style="padding-top: 8px;"><input type="submit" value="${_('save')}"/></dd>
</dl>
</form>