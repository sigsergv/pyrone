# -*- coding: utf-8 -*-
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

import logging
import datetime
import calendar
import pytz #@UnresolvedImport
import time
from math import log as lg

from pyramid.i18n import TranslationString as _
from pyramid.url import route_url
from mako.filters import html_escape
from hurry.filesize import size as hsize
from sqlalchemy import func

from pyrone.models.config import get as get_config
from pyrone.models import DBSession, Article, Tag, Comment
from pyrone.lib import auth, lang
from pyrone.lib.lang import supported_langs

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
        title = '<acronym title="%(help)s">%(title)s</acronym>' % dict(help=html_escape(help), title=html_escape(title))
        
    html = """<dt>%(title)s</dt>
    <div id="error-%(name)s" class="error" style="%(style)s">%(error)s</div>
    <dd><input type="text" name="%(name)s" id="fid-%(name)s" value="%(value)s"/></dd>
    """ % dict(name=name, style=estyle, error=html_escape(error_str), 
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
        tstyle += 'height: %spx' % height
        
    if tstyle != '':
        tstyle = ' style="%s"' % tstyle
        
    if value is None:
        value = ''
        
    if help is not None:
        title = '<acronym title="%(help)s">%(title)s</acronym>' % dict(help=html_escape(help), title=html_escape(title))
        
    html = """<dt>%(title)s</dt>
    <div id="error-%(name)s" class="error" style="%(estyle)s">%(error)s</div>
    <dd><textarea type="text" name="%(name)s" id="fid-%(name)s"%(tstyle)s>%(value)s</textarea></dd>
    """ % dict(name=name, estyle=estyle, tstyle=tstyle, error=html_escape(error_str), 
               value=html_escape(value), title=title)
    
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
        title = '<acronym title="%(help)s">%(title)s</acronym>' % dict(help=html_escape(help), title=html_escape(title))
        
    selector_items = []
    for id, v in all_values:
        selected = ''
        if id == value:
            selected = ' selected="selected"'
        s = '<option value="%s"%s>%s</option>' % (id, selected, v)
        selector_items.append(s)
        
    html = """<dt>%(title)s</dt>
    <div id="error-%(name)s" class="error" style="%(style)s">%(error)s</div>
    <dd><select name="%(name)s" id="fid-%(name)s">%(items)s</select></dd>
    """ % dict(name=name, style=estyle, error=html_escape(error_str), 
               items=''.join(selector_items), title=title)
    
    return html

def form_checkbox(name, title, value, errors, help=None, label=None, label_help=None):
    # ignore errors
    # value must be True|False
    
    if label is not None and label_help is not None:
        label = '<acronym title="%(help)s">%(title)s</acronym>' % dict(help=label_help, title=label)
        
    html = ""
    
    if title is not None:
        html += """<dt>%(title)s</dt>""" % dict(title=title)
    
    cb = '<input type="checkbox" name="%(name)s" id="fid-%(name)s"%(checked)s/>' % dict(name=name, 
        checked=' checked="checked"' if value is True else '')
    if label is not None:
        cb = '<label>%(cb)s %(label)s</label>' % dict(cb=cb, label=label)
        
    html += '<dd>%(cb)s</dd>' % dict(cb=cb)
    return html

def timestamp_to_dt(ts):
    """
    Convert UTC seconds to datetime object
    """
    tz = get_config('timezone') 
    tts = datetime.datetime.utcfromtimestamp(ts) # seconds -> time_struct
    utc_dt = pytz.utc.localize(tts).astimezone(tz) # utc time -> local time
    return utc_dt

def timestamp_to_str(ts, fmt='%Y-%m-%d %H:%M'):
    """
    Convert UTC seconds to time string in local timezone
    """
    tz = get_config('timezone') 
    tts = datetime.datetime.utcfromtimestamp(ts) # seconds -> time_struct
    utc_dt = pytz.utc.localize(tts).astimezone(tz) # utc time -> local time
    
    t_str = utc_dt.strftime(fmt.encode('utf-8')).decode('utf-8')
    
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

def span_info(text, escape=True):
    if escape:
        text = html_escape(text)
    return '<span class="info">%s</span>' % text;

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
    
    if user.has_permission('admin'):
        title = _('Administrator')
        name = '<span title="%(title)s" class="account-admin">%(name)s</span>' % dict(name=name, title=title)
    
    if user.kind == 'twitter':
        link = '<a class="account-twitter" href="http://twitter.com/#!/%(name)s">%(name)s</a>' % dict(name=user.login)
    else:
        link = name
        
    return link

def article_url(request, article):
    return '%s%s/%s' % ( route_url('blog_latest', request), article.shortcut_date, article.shortcut )

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
    url_template = '<a href="%s">__TAG__</a>' % route_url('blog_tag_articles', request, tag='__TAG__')
    for tag in article.tags:
        if tag.tag is None:
            continue
        res.append(url_template.replace('__TAG__', tag.tag))
    
    return ', '.join(res)

_cache = dict()

def get_public_tags_cloud(force_reload=False):
    """
    return tags cloud: list of tuples-pairs ("tag", "tag_weight"), tag_weight - is a number divisible by 5,
    0 <= tag_weight <= 100
    Only for published articles.
    """
    if 'tags_cloud' not in _cache or force_reload:
        dbsession = DBSession()
        q = dbsession.query(func.count(Tag.id), Tag.tag).join(Article).filter(Article.is_draft==False).group_by(Tag.tag)
        items = list()
        counts = list()
        total = 0
        for rec in q.all():
            if rec[0] <= 0:
                continue
            total += rec[0]
            items.append( (rec[1], int(rec[0])) )
            counts.append(int(rec[0]))
        
        if len(counts) != 0:
            min_count = min(counts)
            max_counts = max(counts)

            if min_count == max_counts:
                # i.e. all tags counts are the same, so they have the same weight
                weights = [ (x[0], 50) for x in items ]
            else:
                lmm = lg(max_counts) - lg(min_count)
                
                weights = [ ( x[0], (lg(x[1])-lg(min_count))/lmm ) for x in items ]
                
                weights = [ (x[0], 5*(int(100*x[1])/5)) for x in weights ]
            
            _cache['tags_cloud'] = weights
        else:
            _cache['tags_cloud'] = []
    
    return _cache['tags_cloud']

def get_pages_widget_links(lang_code, force_reload=False):
    
    if 'pages_links' not in _cache or force_reload:
        pages_links = list()
        # fetch from settings, parse, fill cache
        raw = get_config('widget_pages_pages_spec')
        if raw is None:
            raw = ''
        for line in raw.split('\n'):
            line = line.strip()
            if len(line) == 0:
                continue
            # take first char - it will be delimiter
            delim = line[0]
            components = line[1:].split(delim)
            if len(components) != 3:
                continue
            lang, url, title = components
            if not url.startswith('http://') and not url.startswith('https://'):
                continue
            link = dict(lang=lang, url=url, title=title)
            pages_links.append(link)
        _cache['pages_links'] = pages_links
    
    return [x for x in _cache['pages_links'] if x['lang']==lang_code]

def get_not_approved_comments_count():
    dbsession = DBSession()
    cnt = dbsession.query(func.count(Comment.id)).filter(Comment.is_approved==False).scalar()
    return cnt
