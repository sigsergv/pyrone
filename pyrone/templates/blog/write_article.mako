<%inherit file="/blog/base.mako"/>

<%def name="title()">\
  % if c.new_article:
    ${_('Write new article')}
  % else:
    ${_('Edit article')}
  % endif
</%def>

<form action="${c.submit_url}" method="POST" onsubmit="return Pyrone.article.checkForm();">
<dl class="form">

  ${h.form_input_text('title', _('Subject (required)'), c.article.title, c.errors)|n}
  ${h.form_input_text('shortcut', _('Shortcut (required)'), c.article.shortcut, c.errors, _(u'Short string (part of the URL), alphanumeric characters and “-” are recommended.'))|n}
  ${h.form_input_text('published', _('Publishing date and time'), h.timestamp_to_str(c.article.published), c.errors, _('Format: YYYY-MM-DD HH:MM'))|n}
  ${h.form_input_text('tags', _('Tags (comma separated)'), ', '.join(c.tags), c.errors)|n}
  ${h.form_textarea('body', _('Article body (required, <a href="/article-markup-tip-en.html" target="_blank" class="new-window">markup</a> is available)'), c.article.body, c.errors)|n}
  
  ${h.form_checkbox('is_draft', None, c.article.is_draft, None, label=_('draft article'), label_help=_('if checked article will not be available to everyone'))|n}
  ${h.form_checkbox('is_commentable', None, c.article.is_commentable, None, label=_('allow visitors comments'))|n}
  
  <dd><input type="submit" value="${_('save')}"/> <input onclick="Pyrone.article.preview()" type="button" value="${_('preview')}"/></dd>
</dl>
</form>

<div id="eid-article-preview" class="eid-article-preview" style="display: none;"></div>
