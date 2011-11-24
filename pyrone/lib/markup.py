"""
Contains function for supported text markupt languages
"""
import markdown
import re
import logging

log = logging.getLogger(__name__)

MARKUP_CONTINUE_MARKER = "<cut>"

def render_text_markup_mini(text):
    """
    Render text using reduced markup elements set
    """
    md = markdown.Markdown(safe_mode=True, output_format='xhtml')
    return md.convert(text)
    
def render_text_markup(text):
    """
    render article text, return tuple (html_preview, html_body)
    """
    text = pre_render_text_markup(text)
    ind = text.find(MARKUP_CONTINUE_MARKER)
    if ind != -1:
        preview_part = text[:ind]
        complete_text = text.replace(MARKUP_CONTINUE_MARKER, "", 1)
    else:
        preview_part = None
        complete_text = text

    md = markdown.Markdown(
        extensions=["footnotes", "wikilinks"],
        extension_configs={
            # commented because current (2.0.3) version of Python Markdown
            # has bug http://www.freewisdom.org/projects/python-markdown/Tickets/000068
            #'footnotes': [("PLACE_MARKER", "~~~~~~~~")]
                },
        safe_mode=True,
        output_format='xhtml')

    preview_html = None
    if preview_part is not None:
        # remove footnotes from the preview
        preview_part = re.sub('\\[\\^[^\\]]+?\\]', '', preview_part)
        log.debug(preview_part)
        preview_html = md.convert(preview_part)

    complete_html = md.convert(complete_text)

    return (preview_html, complete_html)

storage_img_re = False
storage_img_preview_re = False

def pre_render_text_markup(text):
    """
    Render links to files from the storage including inline pictures from the files storage
    """
    global storage_img_re, storage_img_preview_re

    if storage_img_preview_re is False:
        storage_img_preview_re = re.compile("!(!\[[^\]]+\])\(([^)]+)/m\)")

    if storage_img_re is False:
        storage_img_re = re.compile("!(!\[[^\]]+\])\(([^)]+)\)")
        
    # replace preview images
    text = storage_img_preview_re.sub("[\\1(/files/p/\\2)](/files/f/\\2)", text)

    # replace constructions "!![Alt text](IMGID)" with "![Alt text](/storage/f/IMGID)"
    text = storage_img_re.sub("\\1(/files/f/\\2)", text)
    return text
    

