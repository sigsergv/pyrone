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
  ${h.form_input_text('published', _('Publishing date and time'), h.timestamp_to_str(article.published), errors, _('Format: YYYY-MM-DD HH:MM'))|n}
  ${h.form_input_text('tags', _('Tags (comma separated)'), ', '.join(tags), errors)|n}
  ${h.form_textarea('body', _('Article body (required, <a href="/article-markup-tip-en.html" target="_blank" class="new-window">markup</a> is available)'), article.body, errors)|n}
  
  ${h.form_checkbox('is_draft', None, article.is_draft, None, label=_('draft article'), label_help=_('if checked article will not be available to everyone'))|n}
  ${h.form_checkbox('is_commentable', None, article.is_commentable, None, label=_('allow visitors comments'))|n}
  
  <dd><input type="submit" value="${_('save')}"/> <input onclick="Pyrone.article.preview()" type="button" value="${_('preview')}"/></dd>
</dl>
</form>

<div id="eid-article-preview" class="eid-article-preview" style="display: none;"></div>
