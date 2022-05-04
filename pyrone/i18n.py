# import logging

from pyrone.models import config

# DO NOT LOCALIZE LINES BELOW!
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
    lang = config.get(request, 'ui_lang')
    return lang


def includeme(config):
    config.add_translation_dirs('pyrone:locale/')
    config.set_locale_negotiator(locale_negotiator)
    config.add_subscriber('pyrone.subscribers.add_renderer_globals', 'pyramid.events.BeforeRender')
    config.add_subscriber('pyrone.subscribers.add_localizer', 'pyramid.events.NewRequest')