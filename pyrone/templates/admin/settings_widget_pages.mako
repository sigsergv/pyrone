<%inherit file="/admin/base.mako"/>

<%def name="title()">${_(u'Widget “Pages” parameters')}</%def>

<h2>${_(u'Widget “Pages” parameters')}</h2>
<div class="notify" style="display:none;" id="eid-notify"></div>

<!-- render table, up/down buttons -->

<form action="/" onsubmit="Pyrone_settings_widgets_pagesSave('${url('admin_settings_widget_pages_save_ajax')}'); return false;">
<dl class="form">
  ${h.form_textarea('widget_pages_pages_spec', _('Pages list'), 
  	settings['widget_pages_pages_spec'], errors, \
  	help=_(u'One site definition per line, empty lines are ignored. Incorrect lines are ignored.'), height=200)|n}
  	
  <dd>${_(u'Every line defines one page, here is the sample: '+\
  u'<code><pre>!http://google.com ! Google web search\n!http://yandex.ru ! Search in Yandex</pre></code>')|n}</dd>
  <dd>${_(u'You can use any other character as delimiter instead of <strong>!</strong>, e.g. pipe “|”:'+\
  u'<code><pre>|http://google.com | Google web search\n|http://yandex.ru | Search in Yandex</pre></code>')|n}</dd>
  <dd>${_(u'The main idea is simple: first character in the line is delimiter.')}</dd>


  <dd style="padding-top: 8px;"><input type="submit" value="${_('save')}"/></dd>
</dl>
</form>
