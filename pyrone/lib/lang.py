# -*- coding: utf-8 -*-
"""
Languages (i18n)
"""
import logging

from pylons import request

log = logging.getLogger(__name__)

# DO NOT TRANSLATE! 
_languages = dict( en='english', ru=u'русский' )

def supported_langs():
    return ('en', 'ru')

def lang_title(lang_code):
    return _languages[lang_code]

def fallback_lang():
    return 'en'

def lang():
    lang = fallback_lang()
    if 'ui_lang' in request.cookies:
        lang = request.cookies['ui_lang']
    return lang