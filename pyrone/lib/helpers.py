"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

import logging
import datetime
import calendar
import pytz
import os.path
import re
from math import log as lg

from pyramid import threadlocal
from pyramid.i18n import TranslationString as _
from pyramid.url import route_url
from mako.filters import html_escape
from hurry.filesize import size as hsize
from sqlalchemy import func

from pyrone.version import PYRONE_VERSION
from pyrone.models.config import get as get_config
from pyrone.models.file import get_storage_dirs
from pyrone.models import DBSession, Article, Tag, Comment, File
from pyrone.lib import auth, lang
from pyrone.lib import cache

log = logging.getLogger(__name__)


def form_input_text(name, title, value, errors, help=None):
    estyle = ''
    error_str = ''
    if name not in errors:
        estyle = 'display: none;'
    else:
        error_str = errors[name]

    if value is None:
        value = ''

    if help is not None:
        title = '<acronym title="{help}">{title}</acronym>'.format(help=html_escape(help), title=html_escape(title))

    html = """<dt>{title}</dt>
    <div id="error-{name}" class="error" style="{style}">{error}</div>
    <dd><input type="text" name="{name}" id="fid-{name}" value="{value}"/></dd>
    """.format(name=name, style=estyle, error=html_escape(error_str),
               value=html_escape(value), title=title)

    return html


def form_textarea(name, title, value, errors, help=None, height=None):
    estyle = ''
    tstyle = ''
    error_str = ''
    if name not in errors:
        estyle = 'display: none;'
    else:
        error_str = errors[name]

    if height is not None:
        tstyle += 'height: {0}px'.format(height)

    if tstyle != '':
        tstyle = ' style="{0}"'.format(tstyle)

    if value is None:
        value = ''

    if help is not None:
        title = '<acronym title="{help}">{title}</acronym>'.format(help=html_escape(help), title=html_escape(title))

    html = ''
    if title != '':
        html += '<dt>{title}</dt>\n'.format(title=title)

    html = """<div id="error-{name}" class="error" style="{estyle}">{error}</div>
    <dd><textarea type="text" name="{name}" id="fid-{name}"{tstyle}>{value}</textarea></dd>
    """.format(name=name, estyle=estyle, tstyle=tstyle, error=html_escape(error_str),
               value=html_escape(value))

    return html


def form_selector(name, title, all_values, value, errors, help=None):
    """
    Render html element OPTION
    """
    estyle = ''
    error_str = ''
    if name not in errors:
        estyle = 'display: none;'
    else:
        error_str = errors[name]

    if help is not None:
        title = '<acronym title="{help}">{title}</acronym>'.format(help=html_escape(help), title=html_escape(title))

    selector_items = []
    for id, v in all_values:
        selected = ''
        if id == value:
            selected = ' selected="selected"'
        s = '<option value="{0}"{1}>{2}</option>'.format(id, selected, v)
        selector_items.append(s)

    html = """<dt>{title}</dt>
    <div id="error-{name}" class="error" style="{style}">{error}</div>
    <dd><select name="{name}" id="fid-{name}">{items}</select></dd>
    """.format(name=name, style=estyle, error=html_escape(error_str),
               items=''.join(selector_items), title=title)

    return html


def form_checkbox(name, title, value, errors, help=None, label=None, label_help=None):
    # ignore errors

    if label is not None and label_help is not None:
        label = '<acronym title="{help}">{title}</acronym>'.format(help=label_help, title=label)

    html = ""

    if title is not None:
        html += """<dt>{title}</dt>""".format(title=title)

    cb = '<input type="checkbox" name="{name}" id="fid-{name}"{checked}/>'.format(name=name,
        checked=' checked="checked"' if value is True else '')
    if label is not None:
        cb = '<label>{cb} {label}</label>'.format(cb=cb, label=label)

    html += '<dd>{cb}</dd>'.format(cb=cb)
    return html


def timestamp_to_dt(ts):
    """
    Convert UTC seconds to datetime object
    """
    tz = get_config('timezone')
    tts = datetime.datetime.utcfromtimestamp(ts)  # seconds -> time_struct
    utc_dt = pytz.utc.localize(tts).astimezone(tz)  # utc time -> local time
    return utc_dt


def timestamp_to_str(ts, fmt='%Y-%m-%d %H:%M'):
    """
    Convert UTC seconds to time string in local timezone
    """
    tz = get_config('timezone')
    tts = datetime.datetime.utcfromtimestamp(ts)  # seconds -> time_struct
    utc_dt = pytz.utc.localize(tts).astimezone(tz)  # utc time -> local time

    t_str = utc_dt.strftime(fmt)

    return t_str


def str_to_timestamp(t_str):
    """
    Convert time string in local timezone to UTC seconds
    """
    tz = get_config('timezone')
    dt = datetime.datetime.strptime(t_str, '%Y-%m-%d %H:%M')
    dt_loc = tz.localize(dt)
    dt_utc = dt_loc.astimezone(pytz.utc)

    return calendar.timegm(dt_utc.timetuple())


def dt_to_timestamp(dt):
    """
    Convert datetime (UTC) object to UTC seconds
    """
    return calendar.timegm(dt.timetuple())

def span_info(text, escape=True):
    if escape:
        text = html_escape(text)
    return '<span class="info">{0}</span>'.format(text)


def cond(condition, true_val, false_val):
    return true_val if condition else false_val


def get_setting(request, id, default_value=None):
    s = request.registry.settings
    if id in s:
        return s[id]
    else:
        return default_value


def user_link(user):
    """
    Generate URL for the user, it could be URL pointing to local user account or to
    external account (twitter, google etc)
    """
    name = user.display_name or user.login

    if user.has_role('admin'):
        title = _('Administrator')
        name = '<span title="{title}" class="account-admin">{name}</span>'.format(name=name, title=title)

    if user.kind == 'twitter':
        link = '<a class="account-twitter" href="http://twitter.com/#!/{name}">{name}</a>'.format(name=user.login)
    else:
        link = name

    return link


def article_url(request, article):
    return '{0}{1}/{2}'.format(route_url('blog_latest', request), article.shortcut_date, article.shortcut)


def article_tags(article):
    """
    Generate comma separated list of tags
    """
    res = []
    for tag in article.tags:
        if tag.tag is None:
            continue
        res.append(tag.tag)

    res = ', '.join(res)
    return res


def article_tags_links(request, article):
    """
    Generate comma separated list of tag hyperlinks
    """
    res = []
    url_template = '<a href="{0}">#__TAG__</a>'.format(route_url('blog_tag_articles', request, tag='__TAG__'))
    for tag in article.tags:
        if tag.tag is None:
            continue
        res.append(url_template.replace('__TAG__', tag.tag))

    return ' '.join(res)


def get_public_tags_cloud(force_reload=False):
    """
    return tags cloud: list of tuples-pairs ("tag", "tag_weight"), tag_weight - is a number divisible by 5,
    0 <= tag_weight <= 100
    Only for published articles.
    """
    value = cache.get_value('tags_cloud')
    if value is None or force_reload:
        dbsession = DBSession()
        q = dbsession.query(func.count(Tag.id), Tag.tag).join(Article).filter(Article.is_draft==False).group_by(Tag.tag)
        items = list()
        counts = list()
        total = 0
        for rec in q.all():
            if rec[0] <= 0:
                continue
            total += rec[0]
            items.append((rec[1], int(rec[0])))
            counts.append(int(rec[0]))

        if len(counts) != 0:
            min_count = min(counts)
            max_counts = max(counts)

            if min_count == max_counts:
                # i.e. all tags counts are the same, so they have the same weight
                weights = [(x[0], 50) for x in items]
            else:
                lmm = lg(max_counts) - lg(min_count)

                weights = [(x[0], (lg(x[1])-lg(min_count)) / lmm) for x in items]
                weights = [(x[0], int(5*(int(100*x[1])/5))) for x in weights]

            value = weights
        else:
            value = []

        cache.set_value('tags_cloud', value)

    return value


def get_pages_widget_links(force_reload=False):

    value = cache.get_value('pages_links')

    if value is None or force_reload:
        pages_links = list()
        # fetch from settings, parse, fill cache
        raw = get_config('widget_pages_pages_spec')
        if raw is None:
            raw = ''
        for line in raw.split('\n'):
            line = line.strip()
            if len(line) == 0:
                continue
            # take first char - it's a delimiter
            delim = line[0]
            components = line[1:].split(delim)
            if len(components) != 2:
                continue
            url, title = components
            if not url.startswith('http://') and not url.startswith('https://'):
                continue
            link = {'url': url, 'title': title}
            pages_links.append(link)

        value = pages_links
        cache.set_value('pages_links', value)

    return value


def get_twitter_share_link_button(force_reload=False):
    value = cache.get_value('rendered_twitter_share_link_button')
    if value is None or force_reload:
        if get_config('social_twitter_share_link') != 'true':
            value = ''
        else:
            tpl = '''<a href="https://twitter.com/share" class="twitter-share-button"{twitter_via}{show_count}>Tweet</a>'''

            twitter_via = get_config('social_twitter_share_link_via')
            show_count = get_config('social_twitter_share_link_show_count')
            repl = {
                'twitter_via': 'pyrone',
                'show_count': ''
                }
            if twitter_via != '':
                # possible
                repl['twitter_via'] = ' data-via="{0}"'.format(html_escape(twitter_via))
            if show_count != 'true':
                repl['show_count'] = ' data-count="none"'

            value = tpl.format(**repl)

            value += '''<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>'''

        cache.set_value('rendered_twitter_share_link_button', value)

    return value


def get_gplusone_button(force_reload=False):
    value = cache.get_value('rendered_gplusone_button')
    if value is None or force_reload:
        if get_config('social_gplusone') != 'true':
            value = ''
        else:
            tpl = '''<script type="text/javascript" src="https://apis.google.com/js/plusone.js"></script>
<g:plusone></g:plusone>'''
            value = tpl

        cache.set_value('rendered_gplusone_button', value)

    return value


def get_facebook_share_button_script():
    if get_config('social_facebook_share') != 'true':
        value = ''
    else:
        tpl = '''<!-- facebook share button -->
<div id="fb-root"></div>
<script>(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.8";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>
<!-- facebook share button -->'''
        value = tpl
    return value

def get_facebook_share_button(url):
    if get_config('social_facebook_share') != 'true':
        value = ''
    else:
        tpl = '''<div class="fb-share-button" data-href="{url}" data-layout="button_count"></div>'''
        value = tpl.format(url=url)

    return value


def get_not_approved_comments_count():
    dbsession = DBSession()
    cnt = dbsession.query(func.count(Comment.id)).filter(Comment.is_approved==False).scalar()
    return cnt

def get_supported_langs_spec():
    return lang.supported_langs_spec()

def get_available_themes():
    dbsession = DBSession()
    themes = [
        ('default', _('Default theme (internal)')),
        ('green', _('Green theme (internal)')),
        ('blog.regolit.com', _('blog.regolit.com style (internal)'))]

    # load suitable css files from the storage
    storage_dirs = get_storage_dirs()
    storage_path = storage_dirs['orig']
    style_files = dbsession.query(File).filter(File.dltype=='auto', File.content_type=='text/css').all()
    theme_data_re = re.compile(r'/\* pyrone-theme-data:([0-9a-z-]+):\s*(.+)\s*\*/')

    for f in style_files:
        # open css file and read metadata
        filename = os.path.join(storage_path, f.name)
        description = f.name
        theme_data = {}

        try:
            with open(filename) as fp:
                # analyze first line
                line = fp.readline(100)
                if not line.startswith('/* pyrone-theme-css */'):
                    continue

                # now read remaining file and search for metadata
                for line in fp:
                    mo = theme_data_re.match(line)
                    if mo is None:
                        continue
                    theme_data[mo.group(1)] = mo.group(2)

        except Exception as e:
            log.error(e)
            continue

        # get description from the data
        request = threadlocal.get_current_request()
        key = 'title-{0}'.format(lang.lang(request))
        if key in theme_data:
            description = theme_data[key]

        themes.append((f.name, description))

    return themes

def get_current_theme_css():
    ui_theme = get_config('ui_theme', force=True)
    print(ui_theme)
    css_url = '/static/styles/{0}/blog.css'

    if ui_theme is None:
        ui_theme = 'default'

    if ui_theme.endswith('.css'):
        css_url = '/files/f/{0}'

    return css_url.format(ui_theme)
