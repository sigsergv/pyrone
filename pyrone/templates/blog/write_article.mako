<%inherit file="/blog/base.mako"/>

<%def name="title()">\
  % if new_article:
    ${_('Write new article')}
  % else:
    ${_('Edit article')}
  % endif
</%def>

<form action="${submit_url}" method="POST" onsubmit="return Pyrone.article.checkForm();">
<dl class="form">

  ${h.form_input_text('title', _('Subject (required)'), article.title, errors)|n}
  ${h.form_input_text('shortcut', _('Shortcut (required)'), article.shortcut, errors, _(u'Short string (part of the URL), alphanumeric characters and “-” are recommended.'))|n}
  ${h.form_input_text('published', _('Publishing date and time'), article_published_str, errors, _('Format: YYYY-MM-DD HH:MM'))|n}
  ${h.form_input_text('tags', _('Tags (comma separated)'), ', '.join(tags), errors)|n}
  ${h.form_textarea('body', _('Article body (required, <a href="/static/article-markup-tip-en.html" target="_blank" class="new-window">markup</a> is available)'), article.body, errors)|n}
  
  ${h.form_checkbox('is_draft', None, article.is_draft, None, label=_('draft article'), label_help=_('if checked article will not be available to everyone'))|n}
  ${h.form_checkbox('is_commentable', None, article.is_commentable, None, label=_('allow visitors comments'))|n}
  
  <dd><input type="submit" value="${_('save')}"/>
  % if not new_article:
    <input type="button" id="eid-save-button" onclick="Pyrone.article.save('${save_url_ajax}');" value="${_('save and continue editing')}"/> 
  % endif  
    <input onclick="Pyrone.article.preview();" type="button" value="${_('preview')}"/></dd>
</dl>
</form>

<div id="eid-article-notify" class="notify" style="display:none;"></div>
<div id="eid-article-warning" class="warning" style="display:none;"></div>
<div id="eid-article-render-preview" style="display: none;"></div>
