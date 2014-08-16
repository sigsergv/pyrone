<%inherit file="/blog/base.mako"/>

<%def name="title()">\
  % if new_article:
    ${_('Write new article')}
  % else:
    ${_('Edit article')}
  % endif
</%def>

<form action="${submit_url}" method="POST" id="form" onsubmit="return Pyrone_article_checkForm();">
<dl class="form">

  ${h.form_input_text('title', _('Subject (required)'), article.title, errors)|n}
  ${h.form_input_text('shortcut', _('Shortcut (required)'), article.shortcut, errors, _(u'Short string (part of the URL), alphanumeric characters and “-” are recommended.'))|n}
  ${h.form_input_text('published', _('Publishing date and time'), article_published_str, errors, _('Format: YYYY-MM-DD HH:MM'))|n}
  ${h.form_input_text('tags', _('Tags (comma separated)'), ', '.join(tags), errors)|n}
  ${_('Article body (required, markup: *<em>italic</em>*, **<strong>bold</strong>**, [hyperlink](http://example.com) <a href="/static/article-markup-tip-en.html" target="_blank" class="new-window">more</a>)')|n}

  <!-- body text control buttons -->
  <div class="editor-text-controls">
    <span class="button" onclick="Pyrone_editor_wrap('fid-body', '`');" title="${_('Inline code (monospace text)')}">`$x`</span>
    <span class="button" onclick="Pyrone_editor_wrap('fid-body', '*');" title="${_('Emphasis (italic)')}"><em>I</em>&nbsp;</span>
    <span class="button" onclick="Pyrone_editor_wrap('fid-body', '**');" title="${_('Strong text (bold)')}"><strong>B</strong></span>
    <span class="button" onclick="Pyrone_editor_blockquote('fid-body');" title="${_('Quotation')}">&gt;</span>

##    <span class="button" onclick="Pyrone_editor_unindent('fid-body');" title="${_('Unindent selected block.')}">←¶</span>
##    <span class="button" onclick="Pyrone_editor_indent('fid-body');" title="${_('Indent selected block.')}">¶→</span>
  </div>
  ${h.form_textarea('body', '', article.body, errors)|n}
  
  ${h.form_checkbox('is_draft', None, article.is_draft, None, label=_('draft article'), label_help=_('if checked article will not be available to everyone'))|n}
  ${h.form_checkbox('is_commentable', None, article.is_commentable, None, label=_('allow visitors comments'))|n}
  
  <dd><button class="button" onclick="$('#form').submit(); return false;"><span class="fa fa-save"></span> ${_('save')}</button>

  % if not new_article:
  <button class="button" onclick="Pyrone_article_save('${save_url_ajax}'); return false;">${_('save and continue editing')}</button>
  % endif  
    <button class="button" onclick="Pyrone_article_preview(); return false;"><span class="fa fa-flask"></span> ${_('preview')}</button></dd>
</dl>
</form>

<div id="eid-article-notify" class="notify" style="display:none;"></div>
<div id="eid-article-warning" class="warning" style="display:none;"></div>
<div id="eid-article-render-preview" style="display: none;"></div>
