"""
Languages (i18n)
"""
import logging

from pyrone.models import config

log = logging.getLogger(__name__)

# DO NOT LOCALIZE LINE BELOW!
_languages = {
    'en': u'english', 
    'ru': u'русский'
    }


def supported_langs_spec():
    return _languages

def lang_title(lang_code):
    return _languages[lang_code]


def fallback_lang():
    return 'en'


def locale_negotiator(request):
    lang = config.get('ui_lang')
    return lang

lang = locale_negotiator
