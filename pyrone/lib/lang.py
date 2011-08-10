# -*- coding: utf-8 -*-
"""
Languages (i18n)
"""
import logging

import pyramid.threadlocal as threadlocal

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
    request = threadlocal.get_current_request()
    if 'ui_lang' in request.cookies:
        lang = request.cookies['ui_lang']
    return lang
