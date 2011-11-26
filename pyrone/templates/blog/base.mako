## -*- coding: utf-8 -*-
## vim: shiftwidth=2 tabstop=2
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
  <script src="http://ajax.googleapis.com/ajax/libs/ext-core/3/ext-core.js" language="JavaScript"></script>
  <script language="javascript" src="/static/lang/${h.lang.lang(request)}.js"></script>
  <script language="javascript" src="/static/scripts/blog.js"></script>
  <link rel="icon" type="image/png" href="/favicon.png"/>
  <link rel="stylesheet" type="text/css" href="/static/styles/${h.get_config('site_style')}/blog.css"/>
  <link rel="alternate" type="application/atom+xml" title="${h.get_config('site_title')} - ${_('Latest articles feed')}" href="${url('blog_latest_rss')}"/>
  <title>${self.title()} — ${h.get_config('site_title')}</title>
  <%include file="/widgets/google_analytics.mako"/>
</head>
<body>
<div id="topbar"><div class="title"><a href="/">${h.get_config('site_title')}</a></div></div>
  <div id="contentbar">
    <div id="content">
    ${next.body()}
    </div>
    <div id="bottombar"><div class="title">${h.get_config('site_copyright')} | <a href="http://bitbucket.org/cancel/pyrone">${_('Powered by Pyrone')}</a></div>
    </div>
  </div>

  <div id="sidebar">
    <%include file="/widgets/pages.mako"/>
    <%include file="/widgets/account.mako"/>
    <%include file="/widgets/actions.mako"/>
    <%include file="/widgets/tags_cloud.mako"/>
  </div>
</body>
</html>
